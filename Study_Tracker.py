import datetime
import json
import os
import tkinter as tk
from tkinter import messagebox

DATA_FILE = 'study_data.json'

class StudyTracker:
    def __init__(self):
        if os.path.isfile(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {}
        self.start_time = None
        self.study_in_progress = False
        self.elapsed_time = datetime.timedelta()

    def save_data(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.data, f)

    def add_module(self, module):
        self.data[module] = self.data.get(module, [])
        self.save_data()

    def remove_last_study_time(self, module):
        if module in self.data and self.data[module]:
            self.data[module].pop()
            self.save_data()

    def remove_module(self, module):
        if module in self.data:
            del self.data[module]
            self.save_data()

    def start_or_pause_study(self, module):
        if self.study_in_progress:
            # If study is in progress, pause and calculate elapsed time
            self.elapsed_time += datetime.datetime.now() - self.start_time
            self.study_in_progress = False
            self.start_time = None
        else:
            # If study is not in progress, start it
            self.start_time = datetime.datetime.now()
            self.study_in_progress = True

    def end_study(self, module):
        if self.study_in_progress:
            self.elapsed_time += datetime.datetime.now() - self.start_time
        elapsed_time_hours = self.elapsed_time.total_seconds() / 3600
        self.data[module].append(elapsed_time_hours)
        self.start_time = None
        self.study_in_progress = False
        self.elapsed_time = datetime.timedelta()
        self.save_data()

    def add_past_time(self, module, hours):
        self.data[module].append(hours)
        self.save_data()

    def display_data(self, module=None):
        if module is not None:
            if module not in self.data:
                return f"No data for module: {module}"
            else:
                times = self.data[module]
                total_seconds = sum(times) * 3600  # Convert hours to seconds
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                return f'Module: {module}, Total study time: {int(hours):02d}H:{int(minutes):02d}M:{int(seconds):02d}S\n'
        else:
            total_seconds = sum(t for module in self.data for t in self.data[module]) * 3600
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f'Total study time across all modules: {int(hours):02d}H:{int(minutes):02d}M:{int(seconds):02d}S\n'


class StudyApp:
    def __init__(self, root):
        self.tracker = StudyTracker()
        self.root = root
        self.root.title("Study Tracker")
        self.root.geometry('400x200')

        # Create a StringVar to hold the currently-selected module and timer
        self.current_module = tk.StringVar()
        self.timer = tk.StringVar()

        # Create Timer label
        self.timer_label = tk.Label(root, textvariable=self.timer)
        self.timer_label.pack()

        # Create Module dropdown
        self.module_option = tk.OptionMenu(root, self.current_module, "No modules")
        self.module_option.pack()

        # Create Manage Modules Button
        self.manage_modules_button = tk.Button(root, text="Manage Modules", command=self.manage_modules)
        self.manage_modules_button.pack()


        self.study_in_progress = False  # Add this line
        # Create Study Start and End Buttons
        self.start_or_pause_study_button = tk.Button(root, text="Start/Pause Study", command=self.start_or_pause_study)
        self.start_or_pause_study_button.pack()

        self.end_study_button = tk.Button(root, text="End Study", command=self.end_study)
        self.end_study_button.pack()

        # Create Display Button
        self.display_button = tk.Button(root, text="Display Study Times", command=self.display_data)
        self.display_button.pack()

        # Create Result Label
        self.result_label = tk.Label(root, text="", width=50)
        self.result_label.pack()


        self.update_dropdown()

    def manage_modules(self):
        # Create a new top-level window
        manage_window = tk.Toplevel(self.root)
        manage_window.title("Manage Modules")
        manage_window.geometry(self.root.geometry())  # same dimensions and position as the original window

        # Create a dropdown menu to select the module
        self.module_var = tk.StringVar(manage_window)
        self.module_option = tk.OptionMenu(manage_window, self.module_var, *self.tracker.data.keys())
        self.module_option.pack()

        # Create Hours Label, Entry, and Add Past Time Button
        hours_label = tk.Label(manage_window, text="Past study time (hours):")
        hours_label.pack()

        self.hours_entry = tk.Entry(manage_window)
        self.hours_entry.pack()

        add_past_time_button = tk.Button(manage_window, text="Add Past Time", command=self.add_past_time)
        add_past_time_button.pack()

        # Create a Manage Modules Button
        manage_modules_button = tk.Button(manage_window, text="Manage Modules", command=self.manage_modules_window)
        manage_modules_button.pack()

        # Create a Back Button
        back_button = tk.Button(manage_window, text="Back", command=manage_window.destroy)
        back_button.pack()

        remove_last_study_time_button = tk.Button(manage_window, text="Remove Last Study Time",
                                                  command=self.remove_last_study_time)
        remove_last_study_time_button.pack()

    def manage_modules_window(self):
        # Create a new top-level window for managing modules
        modules_window = tk.Toplevel(self.root)
        modules_window.title("Manage Modules")
        modules_window.geometry(self.root.geometry())  # same dimensions and position as the original window

        # Create New Module Label, Entry, and Add Module Button
        new_module_label = tk.Label(modules_window, text="New Module:")
        new_module_label.pack()

        self.new_module_entry = tk.Entry(modules_window)
        self.new_module_entry.pack()

        add_module_button = tk.Button(modules_window, text="Add Module", command=self.add_module)
        add_module_button.pack()

        # Create Remove Module Label, Entry, and Remove Module Button, now case-insensitive
        remove_module_label = tk.Label(modules_window, text="Remove Module:")
        remove_module_label.pack()

        self.remove_module_entry = tk.Entry(modules_window)
        self.remove_module_entry.pack()

        remove_module_button = tk.Button(modules_window, text="Remove Module",
                                         command=self.remove_module_case_insensitive)
        remove_module_button.pack()

        # Create a Back Button
        back_button = tk.Button(modules_window, text="Back", command=modules_window.destroy)
        back_button.pack()
    def add_past_time(self):
        module = self.module_var.get()
        hours = self.hours_entry.get()
        if module and hours:
            try:
                hours = float(hours)
                self.tracker.add_past_time(module, hours)
            except ValueError:
                messagebox.showerror("Error", "Invalid hours value. Please enter a number.")

    def remove_last_study_time(self):
        module = self.module_var.get()  # Using the module selected in the manage modules window
        if module:
            self.tracker.remove_last_study_time(module)
            self.update_dropdown()  # Optional, if you want to update the main window dropdown menu

    def remove_module_case_insensitive(self):
        module_to_remove = self.remove_module_entry.get().lower()
        if module_to_remove:  # Check if the entry field is not empty
            for module in list(self.tracker.data.keys()):
                if module.lower() == module_to_remove:
                    self.tracker.remove_module(module)
                    self.update_dropdown()
                    messagebox.showinfo("Module Removal", f"Module '{module}' has been removed.")
                    return
            messagebox.showerror("Module Removal", f"Module '{module_to_remove}' not found.")

    def add_module(self):
        module = self.new_module_entry.get()
        if module:
            self.tracker.add_module(module)
            self.update_dropdown()
            messagebox.showinfo("Module Addition", f"Module '{module}' has been added.")

    def remove_module(self):
        module = self.module_entry.get()
        if module:
            self.tracker.remove_module(module)
            self.update_dropdown()



    def start_or_pause_study(self):
        module = self.current_module.get()
        if module:
            self.tracker.start_or_pause_study(module)
            self.update_timer()
            if self.tracker.study_in_progress:
                self.result_label['text'] = f"Study session started/resumed for module: {module}"
            else:
                self.result_label['text'] = f"Study session paused for module: {module}"

    def end_study(self):
        module = self.current_module.get()
        if module:
            self.tracker.end_study(module)
            self.timer.set('')
            self.update_timer()  # update timer label
            self.result_label['text'] = f"Study session ended for module: {module}"

    def display_data(self):
        module = self.current_module.get()
        if module == 'Total Time':
            self.result_label['text'] = self.tracker.display_data(None)
        else:
            self.result_label['text'] = self.tracker.display_data(module)

    def update_timer(self):
        if self.tracker.study_in_progress:
            elapsed_time = datetime.datetime.now() - self.tracker.start_time + self.tracker.elapsed_time
        else:
            elapsed_time = self.tracker.elapsed_time
        hours, remainder = divmod(elapsed_time.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        self.timer.set(f"{int(hours):02d}H:{int(minutes):02d}M:{int(seconds):02d}S")
        if self.tracker.study_in_progress or self.timer.get() != '':
            # continue updating if study is in progress, or the timer isn't already blank
            self.root.after(1000, self.update_timer)

    def update_dropdown(self):
        menu = self.module_option['menu']
        menu.delete(0, 'end')
        for module in self.tracker.data.keys():
            menu.add_command(label=module, command=tk._setit(self.current_module, module))
        menu.add_command(label='Total Time', command=tk._setit(self.current_module, 'Total Time'))


def main():
    root = tk.Tk()
    app = StudyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()


