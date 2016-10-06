
def run_host(host_obj):
    host_status = host_obj.get_alive()
    if host_status is None:
        host_obj.set_alive(True)
        host_obj.first_run()
    elif host_status is False:
        host_obj.toggle_alive(True)
        host_obj.run()
    else:
        host_obj.update()

def kill_host(host_obj):
    host_status = host_obj.get_alive()
    if host_status is True:
        host_obj.kill()

class Host:
    _is_alive = None

    def __init__(self):
        pass
    
    def first_run(self):
        print("test")

    def run(self):
        print("test2")

    def update(self):
        print("test33")

    def kill(self):
        print("test666")

    def set_alive(self, status):
        self._is_alive = status

    def toggle_alive(self):
        self._is_alive = not self._is_alive

    def get_alive(self):
        return self._is_alive