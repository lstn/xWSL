import pythoncom
import win32serviceutil
import win32service
import win32event
import win32api
import servicemanager
import socket
import time
from core import host as xwls_host
import sys

class xWLSWin32HostService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'xWLSWin32HostService'
    _svc_display_name_ = 'xWLS Host Service'
    _svc_description_ = 'Host service for xWLS, allowing Windows Linux Subsystem users to execute Windows commands and executables.'
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)        
        socket.setdefaulttimeout(60)
        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        
    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED, (self._svc_name_, ''))
        self.timeout = 70000     #70 seconds / 1:10 minutes
        self.main()
        
    def main(self):
        f = open('C:\\testpyinstaller.txt', 'a')
        host = xwls_host.Host(fileToWrite=f)
        rc = None
        while rc != win32event.WAIT_OBJECT_0:
            xwls_host.run_host(host) # This is where my logic exists
            f.write('Test Service  \n')
            f.flush()
            #block for 24*60*60 seconds and wait for a stop event
            #it is used for a one-day loop
            rc = win32event.WaitForSingleObject(self.hWaitStop, 24*60*60*1000)

        while True:
            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)

            if rc == win32event.WAIT_OBJECT_0:
                # Stop signal encountered
                servicemanager.LogInfoMsg("xWLS - STOPPED!")
                self._isAlive = False
                break
            else:
                try:
                    # xwls_host.run_host(host)
                    f.flush()
                except:
                    pass

        f.write('shut down \n')
        f.close()
        
        #pass
def ctrlHandler(ctrlType):
   return True
        
if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(xWLSWin32HostService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32api.SetConsoleCtrlHandler(ctrlHandler, True)
        win32serviceutil.HandleCommandLine(xWLSWin32HostService)