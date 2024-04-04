from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import platform
from kivy.properties import StringProperty
from requests.exceptions import ConnectionError
import requests

class FirstWindow(Screen):
    def set_server_address(self, address):
        try:
            if address.strip() == "":
                raise ValueError("Address is empty")
            
            SecondWindow.server_address = address
            dialog = MDDialog(title="Success", 
                            text="Save Successfully", 
                            size_hint=(0.8, 0.3))
            dialog.open()
        except ValueError:
            dialog = MDDialog(title="Error", 
                            text="Please enter an IP address", 
                            size_hint=(0.8, 0.3))
            dialog.open()

class SecondWindow(Screen):
    img_display = ""
    extracted = ""
    server_address = ""  
    result_dialog = ""

    def importImage(self, filename):
        try:
            if filename:
                self.ids.img_display.source = filename[0]
                self.img_display = self.ids.img_display
                self.extract()
        except Exception as e:
            print(e)

    def extract_and_translate(self):
        # Check if self.img_display is not None and if an image has been selected
        if not self.img_display.source:
            dialog = MDDialog(title="Error", 
                            text="Please select an image first.", 
                            size_hint=(0.8, 0.3))
            dialog.open()
            return

        try:
            url = f'http://{self.server_address}/extract_text'
            # Use the file path stored in self.img_display.source
            with open(self.img_display.source, 'rb') as file:
                response = requests.post(url, files={'file': file})
                # Close the file after you're done with it
                file.close()
            if response.status_code == 200:
                self.extracted = str(response.json()["text"])
        except ConnectionError:
            dialog = MDDialog(title="Error", 
                            text="Failed to connect to the server.", 
                            size_hint=(0.8, 0.3))
            dialog.open()
            return

        if not self.extracted:
            dialog = MDDialog(title="Error", 
                            text="No text extracted to translate.", 
                            size_hint=(0.8, 0.3))
            dialog.open()
            return 

        try:
            url = f'http://{self.server_address}/translate'
            response = requests.post(url, json={"text": self.extracted})
            if response.status_code == 200:
                translated_text = str(response.json()["translated_text"])
                dialog = MDDialog(title="Translation Result", 
                                text=f"Cebuano: {self.extracted}\n\nButuanon: {translated_text}", 
                                size_hint=(0.8, 0.3))
                dialog.open()
        except ConnectionError:
            dialog = MDDialog(title="Error", 
                            text="Failed to connect to the server.", 
                            size_hint=(0.8, 0.3))
            dialog.open()


class WindowManager(ScreenManager):
    pass

class MyApp(MDApp):
    def build(self):
        
        if platform == "android":
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

        self.theme_cls.theme_style = "Dark"
        return Builder.load_file("main.kv")
        
    def about_dialog(self, *args):
        dialog = MDDialog(title="About", 
                          text="This is the about dialog.", 
                          size_hint=(0.8, 0.3))
        dialog.open()

    
        
if __name__=="__main__":
    MyApp().run()