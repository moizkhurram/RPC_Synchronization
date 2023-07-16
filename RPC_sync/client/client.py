import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import xmlrpc.client
import os

def get_file_name(path_):

    if '\\' in path_:
        n=path_.split('\\')
        return n[-1]
    
    else:
        n= path_.split('/')
        return n[-1]
    
class MyHandler(FileSystemEventHandler):
    def __init__(self):
        self.events = []

    def on_any_event(self, event):
        if event.event_type=="moved":
            self.events.append((event.event_type, event.src_path,event.dest_path))
        else:
            self.events.append((event.event_type, event.src_path))


def monitor_folder(folder_path):
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(5)
            if event_handler.events:
                print("Actions in the last 5 seconds:")
                event_handler.events=list(dict.fromkeys(event_handler.events))
                
                
                for action in event_handler.events:                    
                    
                    file_name=get_file_name(action[1])
                    
                    if action[0]=='modified':
                        upload_file(file_name)
                    if action[0]=='moved':
                        new_file_name=get_file_name(action[-1])
                        print(file_name,new_file_name)
                        rename_file(file_name,new_file_name)
                    if action[0]=="created":
                        upload_file(file_name)
                    if action[0]=="deleted":
                        delete_file(file_name)
                    
                   
                    

                    

                event_handler.events.clear()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


    

def upload_file(file_name):

    current_path = os.getcwd()
    current_path = current_path.replace("\\", "/")
    current_path=current_path+'/sync_client'
    with open('{}/{}'.format(current_path,file_name), 'rb') as file:
        file_data = file.read()

    proxy = xmlrpc.client.ServerProxy('http://localhost:9000/')  # Adjust the server URL and port
    result = proxy.upload(file_name, xmlrpc.client.Binary(file_data))
    print(f"Upload status: {result}")

def download_file(file_name):
    proxy = xmlrpc.client.ServerProxy('http://localhost:9000/')  # Adjust the server URL and port
    file_data = proxy.download(file_name)
    if file_data is None:
        print(f"File '{file_name}' not found.")
        return

    with open(file_name, 'wb') as file:
        file.write(file_data.data)
    print(f"Downloaded file '{file_name}'")

def delete_file(file_name):
    proxy = xmlrpc.client.ServerProxy('http://localhost:9000/')  # Adjust the server URL and port
    result = proxy.delete(file_name)
    if result:
        print(f"File '{file_name}' deleted.")

    else:
        print(f"File '{file_name}' not found.")

def rename_file(old_name, new_name):
    proxy = xmlrpc.client.ServerProxy('http://localhost:9000/')  # Adjust the server URL and port
    result = proxy.rename(old_name, new_name)
    if result:
        print(f"File '{old_name}' renamed to '{new_name}'.")
    else:
        print(f"File '{old_name}' not found.")

if __name__ == "__main__":

    current_path = os.getcwd()
    current_path = current_path.replace("\\", "/")

    folder_path = current_path+'/sync_client' # Replace with the actual folder path you want to monitor

    observer = Observer()
    thread = threading.Thread(target=monitor_folder, args=(folder_path,))
    thread.start()

    try:
        while thread.is_alive():
            thread.join(timeout=1)
    except KeyboardInterrupt:
        observer.stop()

    thread.join()

