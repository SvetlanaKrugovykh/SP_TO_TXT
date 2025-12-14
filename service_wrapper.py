import win32serviceutil
import win32service
import win32event
import servicemanager
import sys
import os
import subprocess
import time

class SpeechToTextService(win32serviceutil.ServiceFramework):
    _svc_name_ = "SpeechToTextService"
    _svc_display_name_ = "Speech to Text Service"
    _svc_description_ = "Speech to Text transcription service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = True
        self.process = None
        self.log_file = None

    def log(self, message):
        try:
            with open(r'C:\logs\service.log', 'a') as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
        except:
            pass

    def SvcStop(self):
        self.log("Stop requested")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.is_running = False
        if self.process:
            self.log("Terminating process")
            self.process.terminate()
            self.process.wait(timeout=5)

    def SvcDoRun(self):
        self.log("Service starting")
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                            servicemanager.PYS_SERVICE_STARTED,
                            (self._svc_name_, ''))
        self.main()

    def main(self):
        try:
            self.log("main() called")
            os.chdir(r'C:\intelligence\SP_TO_TXT')
            sys.path.insert(0, r'C:\intelligence\SP_TO_TXT\src')
            
            # Create log directory
            log_dir = r'C:\logs'
            os.makedirs(log_dir, exist_ok=True)
            self.log("Log directory ready")
            
            # Open log files
            stdout_file = open(os.path.join(log_dir, 'stdout.log'), 'a')
            stderr_file = open(os.path.join(log_dir, 'stderr.log'), 'a')
            self.log("Log files opened")
            
            # Start process with log redirection
            self.log("Starting process")
            self.process = subprocess.Popen([
                r'C:\intelligence\SP_TO_TXT\venv\Scripts\python.exe',
                r'C:\intelligence\SP_TO_TXT\start_service.py'
            ], stdout=stdout_file, stderr=stderr_file, cwd=r'C:\intelligence\SP_TO_TXT')
            
            self.log(f"Process started with PID {self.process.pid}")
            
            # Wait for process exit or stop signal
            while self.is_running:
                ret = self.process.poll()
                if ret is not None:
                    self.log(f"Process exited with code {ret}")
                    break
                win32event.WaitForSingleObject(self.stop_event, 1000)
            
            stdout_file.close()
            stderr_file.close()
            self.log("Service stopped")
            
        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            import traceback
            self.log(traceback.format_exc())

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(SpeechToTextService)