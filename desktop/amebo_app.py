import os, subprocess, threading, site

site.addsitedir(
    r"C:\Users\Administrator\Desktop\GITHUB_PROJECTS\prmp_websockets\prmp_websockets"
)
site.addsitedir(r"C:\Users\Administrator\Desktop\GITHUB_PROJECTS\prmp_qt")
site.addsitedir(r"C:\Users\Administrator\Desktop\GITHUB_PROJECTS\Amebo\server")


from ui.amebo_ui import *


class PRMP_Reloader:
    """reload ability of a gui app.
    subclass this class and bind Reloader.reload() to an event, or manually call it.
    """

    def __init__(self, app: type):
        self.app = app()
        self.start_reload()

    def runner(self):
        """
        the brain.
        exits the first process, call another process with the environments variables of the current one.
        and sets the PRMP environ variable
        """
        args, env = [os.sys.executable] + os.sys.argv, os.environ
        env["PRMP"] = "RUNNING"
        while True:
            exit_code = subprocess.call(args, env=env, close_fds=False)

            try:
                os.system("cls")
            except:
                try:
                    os.system("clear")
                except:
                    ...

            print(f"{exit_code=}, reloading\n")

    def start_reload(self):
        """
        This is the entry point
        func: function to execute if reloaded

        if PRMP environment variable is not set, it call Reloader.runner
        """
        try:
            if os.environ.get("PRMP") == "RUNNING":
                self.app.start()
            else:
                os.sys.exit(self.runner())
        except Exception as E:
            pass


class AmeboApp(QApplication):
    def __init__(self):
        super().__init__()

        threading.Thread(target=AmeboClientData.load).start()

        self.add_style_sheet(AMEBO_QSS)

        self.win = AmeboUI()
        # self.win = AmeboUI_R()
        self.win.destroyed.connect(self.quit)

    def start(self):
        self.win.show()
        self.exec()


a = AmeboApp()
a.start()
# PRMP_Reloader(AmeboApp)
