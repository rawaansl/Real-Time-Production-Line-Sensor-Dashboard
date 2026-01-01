import sys
import time
import json

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QGroupBox, QTextEdit, QLabel, 
                             QGridLayout, QPushButton, QTabWidget, QInputDialog, 
                             QMessageBox, QLineEdit, QFrame, QCheckBox, QSplashScreen, QFileDialog)

from PyQt6.QtGui import QColor, QFont, QPixmap, QIcon
from PyQt6.QtCore import Qt, QTimer
import pyqtgraph as pg

from sensor_worker import SensorWorker, OfflineReplayWorker, WebSocketWorker

from plyer import notification
import simulator

class Dashboard(QMainWindow):
    def __init__(self):    
        super().__init__()
        self.setWindowTitle("Real-Time Production Line Sensor Dashboard")
        self.resize(1600, 950)
        
        self.setWindowIcon(QIcon("imgs/icon.png"))
        
        self.start_time = time.time()
        self.maintenance_unlocked = False 
        self.timeout_seconds = 600 
        
        self.sensor_config = simulator.load_config()['sensors']
        
        self.plot_data = {name: [] for name in self.sensor_config.keys()}
        self.plot_times = {name: [] for name in self.sensor_config.keys()}
        self.name_to_row = {name: i for i, name in enumerate(self.sensor_config.keys())}
        
        self.session_timer = QTimer()
        
        self.session_timer.setSingleShot(True)
           
        self.session_timer.timeout.connect(self.lock_maintenance_session)  # Lock the Maintenance session on timeout
        
        QApplication.instance().installEventFilter(self)   # Monitor user activity globally 
        # observer pattern 
        
        self.active_alarms = set()
        
        
        # Buffer to store the current session for export
        self.session_archive = []
        
        # Dictionary to track last alert times for rate limiting
        self.last_alert_time = {}
        
        self.init_ui()

    def init_ui(self):

        self.setStyleSheet("""
            QMainWindow { background-color: #1C1C1E; }
            
            /* Tab Styling */
            QTabWidget::pane { border: none; background: transparent; }
            QTabBar::tab {
                background: #2C2C2E; color: #8E8E93; 
                padding: 10px 40px; margin: 5px;
                border-radius: 12px; font-weight: 600; font-family: 'Segoe UI', sans-serif;
            }
            QTabBar::tab:selected { background: #3A3A3C; color: #FFFFFF; }
            
            /* 2. ADD THIS: The Hover State */
            QTabBar::tab:hover:!selected {
                background: #3A3A3C; /* A slightly lighter dark grey than the background */
                color: #FFFFFF;      /* Make text white on hover for better contrast */
}

            /* 3. The Selected State (Already in your code) */
            QTabBar::tab:selected { 
                background: #48484A; /* Even lighter or distinct grey for the active tab */
                color: #FFFFFF; 
            }
            
            /* Modern GroupBox as 'Cards' */
            QGroupBox { 
                color: #FFFFFF; font-weight: 600; border: 1px solid #3A3A3C; 
                border-radius: 18px; margin-top: 30px; font-size: 14px;
                background-color: #2C2C2E; padding: 15px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 20px; padding: 0 10px; top: 5px; }

            /* Table Styling - Entries are Read-Only via setEditTriggers in setup_monitoring_ui */
            QTableWidget { 
                background-color: transparent; color: #FFFFFF; 
                gridline-color: #3A3A3C; border: none; 
                font-size: 13px; outline: none;
            }
            QHeaderView::section { 
                background-color: #3A3A3C; color: #AEAEB2; 
                font-weight: bold; border: none; padding: 8px;
            }
            
            .status-text {
                font-family: 'Segoe UI'; font-size: 15px; font-weight: 600;
            }

          /* 1. Normal State: Green with White Text */
            QPushButton#connectBtn {
                background-color: #00FF00; 
                color: #FFFFFF; 
                border: none;
                border-radius: 14px; 
                padding: 12px; 
                font-weight: bold;
            }

            /* 2. Hover while Green: Lighter Green */
            QPushButton#connectBtn:hover { 
                background-color: #28B33F; 
            }

            /* 3. Checked State (System Connected): Red with White Text */
            QPushButton#connectBtn:checked { 
                background-color: #8B0000; 
                color: #FFFFFF; 
            }

            /* 4. Hover while Red: Darker Red */
            QPushButton#connectBtn:checked:hover { 
                background-color: #660000; 
            }
            

            QTextEdit { 
                background-color: #1C1C1E; color: #D1D1D6; 
                border-radius: 12px; padding: 10px; font-family: 'Consolas';
            }
        /* Global Status Circular Indicator */
            QLabel#globalStatusCircle {
            background-color: #8E8E93; /* Fixed: Removed double hash */
            border-radius: 10px;       /* Half of width/height makes a circle */
            min-width: 20px;
            max-width: 20px;
            min-height: 20px;
            max-height: 20px;
            }

            QLabel#globalStatusText {
                color: #FFFFFF;
                font-size: 14px; /* Adjusted slightly for professional balance */
                font-weight: 800;
                letter-spacing: 1px;
                margin-left: 5px;
            }
            
            QCheckBox { color: #AEAEB2; font-weight: 600; font-size: 13px; }
            QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px; border: 2px solid #3A3A3C; }
            QCheckBox::indicator:checked { background-color: #0A84FF; border: 2px solid #0A84FF; }
        """)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.monitoring_tab = QWidget()
        self.setup_monitoring_ui()
        self.tabs.addTab(self.monitoring_tab, "Monitoring Dashboard")
        
        
        
        self.maintenance_tab = QWidget()
        self.setup_maintenance_ui()
        self.tabs.addTab(self.maintenance_tab, "Maintenance Console")
        
        self.tabs.currentChanged.connect(self.check_tab_access)
        
        self.global_status_circle = QLabel()
        self.global_status_circle.setObjectName("globalStatusCircle")
        self.global_status_circle.setFixedSize(30, 30)
        self.global_status_text = QLabel("SYSTEM OFFLINE")
        self.global_status_text.setObjectName("globalStatusText")
        status_layout = QHBoxLayout()
        status_layout.addWidget(self.global_status_circle)
        status_layout.addWidget(self.global_status_text)
        status_layout.addStretch()
        self.statusBar().addPermanentWidget(QWidget())  # Spacer
        self.statusBar().addPermanentWidget(self.global_status_circle)
        self.statusBar().addPermanentWidget(self.global_status_text)
        
        self.statusBar().setStyleSheet("QStatusBar::item { border: none; }")
        



    def setup_monitoring_ui(self):
        layout = QVBoxLayout(self.monitoring_tab)
        layout.setContentsMargins(25, 20, 25, 25)
    
        

        # Header Bar
        conn_bar = QHBoxLayout()
        self.status_led = QLabel("●  SYSTEM DISCONNECTED")
        self.status_led.setProperty("class", "status-text")
        self.status_led.setStyleSheet("color: #FF453A;") 
        
        self.btn_toggle = QPushButton("Connect System")
        self.btn_toggle.setObjectName("connectBtn")
        self.btn_toggle.setProperty("class", "status-text")
        self.btn_toggle.setCheckable(True)
        self.btn_toggle.setFixedWidth(240)
        self.btn_toggle.clicked.connect(self.handle_connection)
        
        
        
        conn_bar.addWidget(self.status_led); conn_bar.addStretch(); conn_bar.addWidget(self.btn_toggle)
        layout.addLayout(conn_bar)

        # --- Content Layout (Now with only two columns) ---
        upper_layout = QHBoxLayout()
        
        
        # 1. Live Sensors Table  --> requirement 1
        table_group = QGroupBox("Live Sensors")
        tv = QVBoxLayout(table_group)
        self.table = QTableWidget(len(self.sensor_config), 4)
        self.table.setHorizontalHeaderLabels(["Sensor", "Reading", "Time", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tv.addWidget(self.table)
        
        # 2. Alarm Log Table  -->  requirement 2
        alarm_group = QGroupBox("Alarm Logs")
        av = QVBoxLayout(alarm_group)
        self.alarm_table = QTableWidget(0, 4)
        self.alarm_table.setHorizontalHeaderLabels(["Time", "Sensor", "Val", "Type"])
        self.alarm_table.verticalHeader().setVisible(False)
        self.alarm_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.alarm_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        av.addWidget(self.alarm_table)

        # Add only the tables to the upper layout. 
        # Proportions: 60% for Live Sensors, 40% for Alarms.
        upper_layout.addWidget(table_group, 3) 
        upper_layout.addWidget(alarm_group, 2)
        
        layout.addLayout(upper_layout, stretch=2)

        # 3. Graphs Section --> requirement 3
        graph_group = QGroupBox("Real-Time Analytics Visualizer")
        gv = QVBoxLayout(graph_group)
        
        # Grid for the actual plots
        self.graph_grid = QGridLayout()
        self.graph_grid.setSpacing(10)
        
        self.plot_widgets = {}
        self.curves = {}

        brand_blue = QColor("#0A84FF")
        fill_brush = QColor(10, 132, 255, 30) 

        for i, (name, config) in enumerate(self.sensor_config.items()):
            # Create the widget
            pw = pg.PlotWidget(title=name)
            pw.setBackground('#1C1C1E') # Match the window background exactly
            pw.setAntialiasing(True)
            
            # Styling the curve
            pen = pg.mkPen(color=brand_blue, width=2)
            self.curves[name] = pw.plot(pen=pen)
            
            self.curves[name].setFillLevel(0)
            self.curves[name].setBrush(fill_brush)

            # Cleanup axes
            pw.showGrid(x=True, y=True, alpha=0.1)
            pw.getAxis('left').setPen('#8E8E93')
            pw.getAxis('bottom').setPen('#8E8E93')
            
            self.plot_widgets[name] = pw
            
            # Important: Ensure the grid spans correctly
            self.graph_grid.addWidget(pw, 0, i)
            
        gv.addLayout(self.graph_grid)
        layout.addWidget(graph_group, stretch=4)
        
    def setup_maintenance_ui(self):
    # Main horizontal layout to split Sidebar from Logs
        main_layout = QHBoxLayout(self.maintenance_tab)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- LEFT SIDEBAR: CONTROLS ---
        sidebar = QVBoxLayout()
        sidebar.setSpacing(15)

        # Group 1: System Control
        sys_group = QGroupBox("SYSTEM CONTROL")
        sys_vbox = QVBoxLayout(sys_group)
        
        self.btn_restart = QPushButton("RESTART SIMULATOR")
        self.btn_clear_alarms = QPushButton("CLEAR ALARM HISTORY")
        
        danger_style = """
            QPushButton {
                background-color: #3A3A3C; color: #FFFFFF; border: 1px solid #48484A;
                border-radius: 6px; padding: 12px; font-weight: bold; font-size: 10px;
            }
            QPushButton:hover { background-color: #FF453A; border-color: #FF453A; }
        """
        self.btn_restart.setStyleSheet(danger_style)
        self.btn_clear_alarms.setStyleSheet(danger_style)
        self.btn_restart.clicked.connect(self.restart_simulation)
        self.btn_clear_alarms.clicked.connect(self.clear_system_alarms)
        
        sys_vbox.addWidget(self.btn_restart)
        sys_vbox.addWidget(self.btn_clear_alarms)

        # Group 2: Preferences
        pref_group = QGroupBox("PREFERENCES")
        pref_vbox = QVBoxLayout(pref_group)
        self.notif_checkbox = QCheckBox("Enable Desktop Alerts")
        self.notif_checkbox.setChecked(False)
        pref_vbox.addWidget(self.notif_checkbox)

        # Add groups to sidebar
        sidebar.addWidget(sys_group)
        sidebar.addWidget(pref_group)
        sidebar.addStretch() # Pushes everything to the top

        # --- RIGHT SIDE: LOG CONSOLE ---
        log_container = QWidget()
        log_layout = QVBoxLayout(log_container)
        log_layout.setContentsMargins(0, 0, 0, 0)

        # Log Header with Title and Clear Button on the same line
        log_header = QHBoxLayout()
        log_title = QLabel("LIVE LOG VIEWER")
        log_title.setStyleSheet("color: #8E8E93; font-weight: 800; font-size: 11px; letter-spacing: 1px;")
        
        self.btn_clear_logs = QPushButton("CLEAR LOGS")
        self.btn_clear_logs.setFixedWidth(100)
        self.btn_clear_logs.setStyleSheet("""
            QPushButton { 
                color: #0A84FF; background: #1C1C1E; border: 1px solid #0A84FF; 
                border-radius: 4px; font-size: 9px; font-weight: bold; 
            }
            QPushButton:hover { background: #0A84FF; color: #FFFFFF; }
        """)
        self.btn_clear_logs.clicked.connect(lambda: self.log_display.clear())

        log_header.addWidget(log_title)
        log_header.addStretch()
        log_header.addWidget(self.btn_clear_logs)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("""
            QTextEdit { 
                background-color: #000000; border: 1px solid #3A3A3C; 
                border-radius: 8px; color: #32D74B; font-family: 'Consolas', 'Courier New';
            }
        """)

        log_layout.addLayout(log_header)
        log_layout.addWidget(self.log_display)
        
         # offline data management section
        data_group = QGroupBox("DATA ARCHIVE")
        data_vbox = QVBoxLayout(data_group)
        
        self.btn_load_offline = QPushButton("OPEN OFFLINE LOG")
        self.btn_load_offline.setStyleSheet("""
            QPushButton { 
                background-color: #0A84FF; color: white; border: none; 
                padding: 10px; font-weight: bold; border-radius: 6px;
            }
            QPushButton:hover { background-color: #5EA8FF; }
        """)
        self.btn_load_offline.clicked.connect(self.load_offline_data)
        data_vbox.addWidget(self.btn_load_offline)
        
        
        self.btn_export_data = QPushButton("EXPORT CURRENT SESSION")
        self.btn_export_data.setStyleSheet("""
            QPushButton { 
                background-color: #32D74B; color: white; border: none; 
                padding: 10px; font-weight: bold; border-radius: 6px;
            }
            QPushButton:hover { background-color: #28B33F; }
        """)
        self.btn_export_data.clicked.connect(self.export_session_to_json)
        data_vbox.addWidget(self.btn_export_data)
        
        
        sidebar.addWidget(data_group)
        


        # Assemble Main UI
        main_layout.addLayout(sidebar, 1) # Sidebar takes 1 part width
        main_layout.addWidget(log_container, 3) # Log takes 3 parts width
        
       

    def clear_system_alarms(self):
        """Logic to clear the history on the Monitoring tab"""
            
        self.alarm_table.setRowCount(0)
        self.update_log("USER ACTION: Alarm history cleared.")


    def restart_simulation(self):
        """Logic to reset the worker and data buffers"""
        
        self.update_log("SYSTEM: Initializing Simulator Restart...")
        
        # 1. Stop worker if it exists
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait() # Ensure it's fully closed
        
        
        # 2. Clear local data buffers so graphs start from zero
        for name in self.plot_data:
            self.plot_data[name] = []
            self.plot_times[name] = []
            
        # 3. Clear the live sensor table
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                self.table.setItem(row, col, QTableWidgetItem(""))
                self.table.item(row, col).setBackground(QColor(255, 255, 255, 0)) # Reset background color
                
        # 4. Clear the plots
        for name in self.curves:
            self.curves[name].setData([], [])
            
            
        self.alarm_table.setRowCount(0)  # Clear alarm history table
        self.active_alarms.clear()      # Clear active alarms set
        self.notif_checkbox.setChecked(False)  # Reset notification preference
        
        
        # Reset global status indicator
        grey_circle_style = "background-color: #8E8E93; border-radius: 10px; min-width: 20px; max-width: 20px; min-height: 20px; max-height: 20px;"
        self.global_status_circle.setStyleSheet(grey_circle_style)
        
        self.global_status_text.setText("SYSTEM OFFLINE")
        self.btn_toggle.setText("Connect System")
        self.status_led.setText("●  SYSTEM DISCONNECTED")
        self.status_led.setStyleSheet("color: #FF453A;")
        
        self.session_timer.stop()  # Stop any existing timers
        self.maintenance_unlocked = False  # Lock maintenance session
        
        
        # 5. Toggle the connect button to trigger a fresh start
        if self.btn_toggle.isChecked():
            
            self.handle_connection() # This will restart it if checked
            
        self.session_archive = []  # Clear the session archive buffer
    
  
        
        self.update_log("SYSTEM: Simulator re-initialized successfully.")
        


    def handle_connection(self):
        
      # Check if a worker exists and is currently running
        if hasattr(self, 'worker') and self.worker.isRunning():
        
        # Use isinstance to identify the type of worker
            if isinstance(self.worker, OfflineReplayWorker):
                self.update_log("SYSTEM: Terminating Offline Replay to switch to Live mode.")
            
        
            # Gracefully stop the thread
            self.worker.stop()
            self.worker.wait() # Critical: ensures the thread is fully dead before starting a new one
            
            
        if self.btn_toggle.isChecked():
            
            # self.worker = SensorWorker()  # TCP sensor Socket Worker initiation if connect system clicked
            
            self.worker = WebSocketWorker()  # WebSocket Worker initiation if connect system clicked
            self.global_status_update(True)
            
            
            # data_received is a pyqtsignal, a messenger from worker thread to main thread carrying sensor data
            # connect is the action of linking the signal to a slot (function) in main thread "link the signal to a specific action"
            self.worker.data_received.connect(self.update_dashboard)
            #update_dashboard is the slot function in main thread that processes incoming sensor data and updates the GUI accordingly
            
            
            self.worker.log_message.connect(self.update_log)
            
            self.worker.start() # start the worker thread, which begins its run() method
            # the OS here is commanded to allocate resources and schedule a new execution thread for the worker besides the main GUI thread
            
            self.btn_toggle.setText("Disconnect System")
            
            if isinstance(self.worker, WebSocketWorker):
                self.status_led.setText("●  WEBSOCKET MODE")
                self.status_led.setStyleSheet("color: #0A84FF;")

            else:
                self.status_led.setText("●  SYSTEM CONNECTED")
                self.status_led.setStyleSheet("color: #32D74B;") 
            
            
        else:
            if hasattr(self, 'worker'): self.worker.stop()
            self.btn_toggle.setText("Connect System")
            self.status_led.setText("●  SYSTEM DISCONNECTED")
            self.status_led.setStyleSheet("color: #FF453A;")
            self.global_status_update(False)

    def update_dashboard(self, sensor_list):
        curr_time = time.time() - self.start_time

        # We save the whole list once per update, not once per sensor.
        if hasattr(self, 'worker') and self.worker.isRunning():
            archive_entry = {
                "timestamp_unix": time.time(),
                "sensors": sensor_list
            }
            self.session_archive.append(archive_entry)
            


      
        # 2. UI UPDATES: Loop through each sensor to update tables/graphs
        for sensor in sensor_list:
            name, val, status, ts = sensor['name'], sensor['value'], sensor['status'], sensor['timestamp']
            row = self.name_to_row.get(name)
            
            if row is not None:
                # Update Table Text
                self.table.setItem(row, 0, QTableWidgetItem(name))
                self.table.setItem(row, 1, QTableWidgetItem(f"{val:.2f}"))
                self.table.setItem(row, 2, QTableWidgetItem(ts))
                disp = "FAULT" if "ALARM" in status else "OK"
                self.table.setItem(row, 3, QTableWidgetItem(disp))

                # Logic for Alarms and Row Backgrounds
                if "ALARM" in status:
                    bg = QColor(255, 69, 58, 40) # Red tint
                    self.global_status_update(False)
                    self.add_to_alarm_history(ts, name, val, status)
                    
                    if name not in self.active_alarms:
                        self.active_alarms.add(name)
                        self.trigger_desktop_alert(name, val, status)
                else:
                    bg = QColor(255, 255, 255, 5) # Default subtle tint
                    self.global_status_update(True)
                    if name in self.active_alarms:
                        self.active_alarms.remove(name)

                # Apply background color to the row
                for col in range(4): 
                    item = self.table.item(row, col)
                    if item: 
                        item.setBackground(bg)

                # Update Individual Graphs
                self.plot_data[name].append(val)
                self.plot_times[name].append(curr_time)
                
                # Sliding window logic (20 seconds)
                while self.plot_times[name] and self.plot_times[name][0] < curr_time - 20:
                    self.plot_times[name].pop(0)
                    self.plot_data[name].pop(0)
                
                self.curves[name].setData(self.plot_times[name], self.plot_data[name])
                self.plot_widgets[name].setXRange(curr_time - 20, curr_time, padding=0)




    def add_to_alarm_history(self, ts, name, val, status):
        self.alarm_table.insertRow(0)
        for i, txt in enumerate([ts, name, f"{val:.2f}", status]):
            item = QTableWidgetItem(txt)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.alarm_table.setItem(0, i, item)
            
            
            
            

    def trigger_desktop_alert(self, name, val, status):
        if not self.notif_checkbox.isChecked():
            return 

        current_time = time.time()
        cooldown_period = 60  # 1 minute between notifications for the SAME sensor
    # Check if we have sent an alert for this specific sensor recently
        last_sent = self.last_alert_time.get(name, 0)
    
        if current_time - last_sent < cooldown_period:
        # It's too soon! Log it internally, but don't spam the OS
            return 

        try:
            notification.notify(
                title=f"⚠️ {status}",
                message=f"{name} is at {val:.2f}",
                app_name="Sensor Dashboard",
                timeout=2
            )
            # Update the timestamp so we don't alert again for 60s
            self.last_alert_time[name] = current_time
        
        except Exception as e:
            print(f"Notification failed: {e}")

    def update_log(self, msg):
        self.log_display.append(f"<b>{time.strftime('%H:%M:%S')}</b> > {msg}")


        # OVERRIDE EVENT FILTER TO RESET TIMER ON USER ACTIVITY
    def eventFilter(self, obj, event):
        if event.type() in [event.Type.MouseMove, event.Type.MouseButtonPress, event.Type.KeyPress]:
            if self.maintenance_unlocked: self.session_timer.start(self.timeout_seconds * 1000)
        return super().eventFilter(obj, event)   # Pass the event to the base class for normal processing 



    def lock_maintenance_session(self):
        if self.maintenance_unlocked:
            self.maintenance_unlocked = False
            self.tabs.setCurrentIndex(0)



    def check_tab_access(self, index):
        if index == 1 and not self.maintenance_unlocked:
            self.tabs.blockSignals(True); self.tabs.setCurrentIndex(0); self.tabs.blockSignals(False)
            token, ok = QInputDialog.getText(self, "Identity Verification", "Enter Admin Token:", echo=QLineEdit.EchoMode.Password)
            if ok and token == "admin123":

                QMessageBox.information(self, "Access Granted", "Maintenance mode activated")
                
                self.maintenance_unlocked = True
                self.session_timer.start(self.timeout_seconds * 1000)
                self.tabs.setCurrentIndex(1)
                
            else:
                QMessageBox.warning(self, "Access Denied", "Invalid token. Access to Maintenance Console is restricted.")
                
    def global_status_update(self, operational):
        if operational:
            self.global_status_circle.setStyleSheet("background-color: #32D74B;")
            self.global_status_text.setText("GLOBAL STATUS INDICATOR")
        else:
            self.global_status_circle.setStyleSheet("background-color: #FF453A;")
            self.global_status_text.setText("GLOBAL STATUS INDICATOR")



    def load_offline_data(self):
        
        # 1. STOP THE LIVE WORKER FIRST
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.update_log("SYSTEM: Suspending Live Worker for Offline Replay...")
            self.worker.stop()
            self.worker.wait() # Wait for the thread to actually close

        # 2. Reset the UI for a fresh start
        self.clear_system_alarms()
        self.log_display.clear()
                
        # clear live sensor table
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                self.table.setItem(row, col, QTableWidgetItem(""))
                self.table.item(row, col).setBackground(QColor(255, 255, 255, 0)) # Reset background color
                
        
        # change system connectivity button to replay mode
        self.btn_toggle.setChecked(False)
        self.btn_toggle.setText("Connect System")
        self.status_led.setText("●  OFFLINE REPLAY MODE")
        self.status_led.setStyleSheet("color: #FFD60A;")
        

        
        # clear the plots
        for name in self.curves:
            self.curves[name].setData([], [])
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Sensor Log", "", "JSON Files (*.json);;CSV Files (*.csv)"
        )
        
        if file_path:
            self.update_log(f"USER: Opening offline archive {file_path}")
            
            
            # Initialize the Offline Worker
            self.worker = OfflineReplayWorker(file_path)   # overwrite the existing live sensor worker
            self.worker.data_received.connect(self.update_dashboard)
            self.worker.log_message.connect(self.update_log)
            self.worker.start() 
            
            
            
    def export_session_to_json(self):

        if not self.session_archive:
            QMessageBox.warning(self, "Export Failed", "No data has been collected in this session yet.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Sensor Data", f"Session_{int(time.time())}.json", "JSON Files (*.json)"
        )

        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.session_archive, f, indent=4)
                
                self.update_log(f"SUCCESS: Exported {len(self.session_archive)} packets to {file_path}")
                QMessageBox.information(self, "Export Complete", f"Successfully saved to {file_path}")
            except Exception as e:
                self.update_log(f"EXPORT ERROR: {str(e)}")       
        
        
    def closeEvent(self, event):
        print("Shutting down system...")

        # 1. Stop the Sensor Worker
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait() # Wait for the thread to fully exit memory
            

        # 3. Accept the close event to actually close the window
        event.accept()
            
            
            
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 1. Create a SOLID background canvas (600x400)
    # This prevents the "overlap" with your desktop
    splash_width, splash_height = 500, 300
    canvas = QPixmap(splash_width, splash_height)
    canvas.fill(QColor("#1C1C1E")) # Matches your Dashboard's dark grey

    # 2. Load and draw your logo onto that canvas
    logo_pix = QPixmap("imgs/logo.png")
    if not logo_pix.isNull():
        logo_pix = logo_pix.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        from PyQt6.QtGui import QPainter
        painter = QPainter(canvas)
        # Calculate center position for the logo
        lx = (splash_width - logo_pix.width()) // 2
        ly = (splash_height - logo_pix.height()) // 2 - 30
        painter.drawPixmap(lx, ly, logo_pix)
        painter.end()

    # 3. Initialize the splash with our solid canvas
    splash = QSplashScreen(canvas)
    
    # 4. Show and add the text
    splash.show()
    # Using a custom font for the message
    splash.setFont(QFont("Segoe UI", 10))
    splash.showMessage("Real-Time Production Line Sensor Dashboard\nInitializing System Components...", 
                       Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, 
                       Qt.GlobalColor.white)

    # 5. Simulate "Loading"
    app.processEvents()
    time.sleep(2.5) 

    # 6. Launch Main Window
    window = Dashboard()   # triggers __init__ of Dashboard class 
    window.show()

    splash.finish(window)
    sys.exit(app.exec())
