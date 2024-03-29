# Imports--------------------------------------------------------------------
from tkinter import (filedialog, StringVar, Tk, Menu, E, W, N, S, LabelFrame, PhotoImage, NORMAL, END,
                     DISABLED, Checkbutton, Label, ttk, scrolledtext, messagebox, OptionMenu, Toplevel, Text, SUNKEN,
                     HORIZONTAL, WORD, Entry, Button, Frame, Spinbox, CENTER)
import subprocess, pyperclip, shutil, pathlib, threading, urllib.request, ssl
from Packages.youtube_dl_about import openaboutwindow
from configparser import ConfigParser
from time import sleep
from re import sub as resub
# This creates an ini file for the auto-downloader ####
from Packages.downloadlinks import download_link_script
download_link_script()
#######################################################
# -------------------------------------------------------------------- Imports

# Main Gui & Windows ---------------------------------------------------------------------------------------
def main_exit_function():  # Asks if the user is ready to exit
    confirm_exit = messagebox.askyesno(title='Prompt', message="Are you sure you want to exit the program?\n\n"
                                                               "     Note: This will end all current tasks!",
                                       parent=main)
    if confirm_exit == False:
        pass
    elif confirm_exit == True:
        try:
            subprocess.Popen(f"TASKKILL /F /im Youtube-DL-GUi.exe /T", creationflags=subprocess.CREATE_NO_WINDOW)
            main.destroy()
        except:
            main.destroy()

# Main UI window ---------------------------------------------------------------------------------------------
main = Tk()
main.title("Youtube-DL-Gui v1.36.1")
main.iconphoto(True, PhotoImage(file="Runtime/Images/Youtube-DL-Gui.png"))
main.configure(background="#434547")
window_height = 580
window_width = 720
screen_width = main.winfo_screenwidth()
screen_height = main.winfo_screenheight()
x_coordinate = int((screen_width / 2) - (window_width / 2))
y_coordinate = int((screen_height / 2) - (window_height / 2))
main.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
main.protocol('WM_DELETE_WINDOW', main_exit_function)

for n in range(4):  # Loop to specify the needed column/row configures
    main.grid_columnconfigure(n, weight=1)
for n in range(5):
    main.grid_rowconfigure(n, weight=1)

# Bundled Apps ---------------------------------------------------------------
config_file = 'Runtime/ytconfig.ini'  # Creates (if doesn't exist) and defines location of config.ini
config = ConfigParser()
config.read(config_file)

if not config.has_section('ffmpeg_path'):
    config.add_section('ffmpeg_path')
if not config.has_option('ffmpeg_path', 'path'):
    config.set('ffmpeg_path', 'path', '')
if not config.has_section('youtubedl_path'):
    config.add_section('youtubedl_path')
if not config.has_option('youtubedl_path', 'path'):
    config.set('youtubedl_path', 'path', '')
if not config.has_section('debug_option'):
    config.add_section('debug_option')
if not config.has_option('debug_option', 'option'):
    config.set('debug_option', 'option', '')
if not config.has_section('close_custom_window_auto'):
    config.add_section('close_custom_window_auto')
if not config.has_option('close_custom_window_auto', 'option'):
    config.set('close_custom_window_auto', 'option', 'off')
try:
    with open(config_file, 'w') as configfile:
        config.write(configfile)
except:
    messagebox.showinfo(parent=main, title='Error', message='Could Not Write to config.ini file\nDelete and Try Again')

pathlib.Path('Apps/yt-dlp').mkdir(parents=True, exist_ok=True)  # Make directory if needed
pathlib.Path('Apps/ffmpeg').mkdir(parents=True, exist_ok=True)  # Make directory if needed

ffmpeg = config['ffmpeg_path']['path']
youtube_dl_cli = config['youtubedl_path']['path']

# --------------------------------------------------------------- Bundled Apps

# Updates youtube-dl.exe -------------------------------------
def check_for_update():
    command = '"' + youtube_dl_cli + '" --update'
    if shell_options.get() == 'Default':
        main.wm_attributes('-alpha', 0.7)
        update_yt_exe = subprocess.Popen('cmd /c ' + command, universal_newlines=True,
                                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                              stdin=subprocess.DEVNULL,
                                              creationflags=subprocess.CREATE_NO_WINDOW)
        update_string = update_yt_exe.communicate()[0]
        messagebox.showinfo(parent=main, title='Info', message=str(update_string))
        main.wm_attributes('-alpha', 1.0)
    elif shell_options.get() == 'Debug':
        subprocess.Popen('cmd /k' + command)

#  ------------------------------------- Updates youtube-dl.exe

# Menu Items and Sub-Bars ---------------------------------------------------------------------------------------------
my_menu_bar = Menu(main, tearoff=0)
main.config(menu=my_menu_bar)

file_menu = Menu(my_menu_bar, tearoff=0, activebackground='dim grey')
my_menu_bar.add_cascade(label='File', menu=file_menu)
file_menu.add_command(label='Exit', command=main_exit_function)

options_menu = Menu(my_menu_bar, tearoff=0, activebackground='dim grey')
my_menu_bar.add_cascade(label='Options', menu=options_menu)

options_submenu = Menu(main, tearoff=0, activebackground='dim grey')
options_menu.add_cascade(label='Shell Options', menu=options_submenu)
shell_options = StringVar()
shell_options.set(config['debug_option']['option'])
if shell_options.get() == '':
    shell_options.set('Default')
elif shell_options.get() != '':
    shell_options.set(config['debug_option']['option'])
def update_shell_option():
    try:
        config.set('debug_option', 'option', shell_options.get())
        with open(config_file, 'w') as configfile:
            config.write(configfile)
    except:
        pass
update_shell_option()
options_submenu.add_radiobutton(label='Progress Bars', variable=shell_options,
                                value="Default", command=update_shell_option)
options_submenu.add_radiobutton(label='CMD Shell (Debug)', variable=shell_options,
                                value="Debug", command=update_shell_option)
options_menu.add_separator()

def set_ffmpeg_path():
    global ffmpeg
    path = filedialog.askopenfilename(title='Select Location to "ffmpeg.exe"', initialdir='/',
                                      filetypes=[('ffmpeg', 'ffmpeg.exe')], parent=main)
    if not path:  # Closes program if 'Cancel' is selected when defining the path with message
        if pathlib.Path(ffmpeg.replace('"', '')).exists():
            pass
        else:
            messagebox.showerror(parent=main, title='Error', message='Program cannot '
                                                                     'post process without "ffmpeg.exe"')
    if path:  # If 'Okay' is selected program will write path to ffmpeg to config.ini
        ffmpeg = '"' + str(pathlib.Path(path)) + '"'
        config.set('ffmpeg_path', 'path', ffmpeg)
        with open(config_file, 'w') as configfile:
            config.write(configfile)

options_menu.add_command(label='Set path to ffmpeg', command=set_ffmpeg_path)

def set_youtubedl_path():
    global youtube_dl_cli
    path = filedialog.askopenfilename(parent=main, title='Select Location to "yt-dlp.exe"', initialdir='/',
                                      filetypes=[('yt-dlp', 'yt-dlp.exe')])
    if not path:  # Closes program if 'Cancel' is selected when defining the path with message
        if pathlib.Path(youtube_dl_cli.replace('"', '')).exists():
            pass
        else:
            messagebox.showerror(parent=main, title='Error', message='Program cannot function without yt-dlp!')
            main.destroy()
    if path:  # If 'Okay' is selected program will write path to youtube-dl to config.ini
        youtube_dl_cli = '"' + str(pathlib.Path(path)) + '"'
        config.set('youtubedl_path', 'path', youtube_dl_cli)
        with open(config_file, 'w') as configfile:
            config.write(configfile)

options_menu.add_command(label='Set path to yt-dlp', command=set_youtubedl_path)
options_menu.add_separator()

def reset_config():
    msg = messagebox.askyesno(title='Warning', message='Are you sure you want to reset the config.ini file settings?')
    if msg == False:
        pass
    if msg == True:
        try:
            config.set('ffmpeg_path', 'path', '')
            config.set('youtubedl_path', 'path', '')
            with open(config_file, 'w') as configfile:
                config.write(configfile)
            messagebox.showinfo(title='Prompt', message='Please restart the program')
        except:
            pass
        main.destroy()

options_menu.add_command(label='Reset Configuration File', command=reset_config)

tools_submenu = Menu(my_menu_bar, tearoff=0, activebackground='dim grey')
my_menu_bar.add_cascade(label='Tools', menu=tools_submenu)
tools_submenu.add_command(label="Check for yt-dlp for updates", command=check_for_update)
tools_submenu.add_separator()

# Function and GUI button to 'Show All Formats' -----------------------------------------------------------------------
def show_formats():
    global download_link, stream_window
    try:
        command = '"' + youtube_dl_cli + ' -F ' + download_link + '"'
        run = subprocess.Popen('cmd /c ' + command, creationflags=subprocess.CREATE_NO_WINDOW,
                               universal_newlines=True,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
        try:
            stream_window.destroy()
        except:
            pass
        stream_window = Toplevel()
        stream_window.title("All Formats")
        stream_window.configure(background="#434547")
        Label(stream_window, text='- ' * 30 + 'Formats ' + '- ' * 30, font=("Times New Roman", 16),
              background='#434547', foreground="white").grid(column=0, row=0)
        show_format_text = scrolledtext.ScrolledText(stream_window, width=120, height=35, tabs=10)
        show_format_text.grid(column=0, pady=10, padx=10)
        show_format_text.configure(state=NORMAL)
        for line in run.stdout:
            show_format_text.insert(END, line)
        show_format_text.configure(state=DISABLED)
    except NameError:
        messagebox.showerror(title='Error', message='Please Paste a Video Link First')

# -------------------------------------------------------------------------------------------------------- Show Formats

tools_submenu.add_command(label="List Avaliable Formats", command=show_formats)

help_menu = Menu(my_menu_bar, tearoff=0, activebackground="dim grey")
my_menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="About", command=openaboutwindow)

# --------------------------------------------------------------------------------------------- Menu Items and Sub-Bars

# Link Frame ----------------------------------------------------------------------------------------------------------
link_frame = LabelFrame(main, text=' Paste Link ')
link_frame.grid(row=0, columnspan=4, sticky=E + W, padx=20, pady=(10, 4))
link_frame.configure(fg="white", bg="#434547", bd=3)
link_frame.rowconfigure(1, weight=1)
link_frame.columnconfigure(0, weight=1)
link_frame.columnconfigure(1, weight=1)

# ---------------------------------------------------------------------------------------------------------- Link Frame

# Input Frame ----------------------------------------------------------------------------------------------------------
input_frame = LabelFrame(main, text=' Input ')
input_frame.grid(row=1, columnspan=4, sticky=E + W, padx=20, pady=(4, 10))
input_frame.configure(fg="white", bg="#434547", bd=3)
input_frame.rowconfigure(1, weight=1)
input_frame.columnconfigure(0, weight=1)
input_frame.columnconfigure(1, weight=1)
link_input_label = Label(input_frame, text='Please Paste Link Above and Select "Add Link"',
                         background="#434547", foreground="white", height=1, font=("Helvetica", 10))
link_input_label.grid(row=0, column=0, columnspan=4, padx=8, pady=(4, 7), sticky=W + E)

# ---------------------------------------------------------------------------------------------------------- Input Frame

# Notebook Frame ------------------------------------------------------------------------------------------------------
tabs = ttk.Notebook(main, height=200)
tabs.grid(row=2, column=0, columnspan=4, sticky=E + W + N + S, padx=20, pady=(10, 0))
general_frame = Frame(tabs, background="#434547")
video_frame = Frame(tabs, background="#434547")
audio_frame = Frame(tabs, background="#434547")
tabs.add(general_frame, text='  General Settings  ')
tabs.add(video_frame, text='  Video Settings  ')
tabs.add(audio_frame, text='  Audio Settings  ')

# ------------------------------------------------------------------------------------------------------ Notebook Frame

# Add Link to variable ------------------------------------------------------------------------------------------------
def apply_link():
    global download_link, extracted_title_name, link_input_label
    link_entry.config(state=NORMAL)  #
    link_entry.delete(0, END)  # This function clears entry box in order to add new link to entry box
    link_entry.config(state=DISABLED)  #
    download_link = text_area.get(1.0, END).rstrip("\n")  # Pasted download link and strips the unneeded newline
    text_area.delete(1.0, END)  # Deletes entry box where you pasted your link as it stores it into var
    link_entry.config(state=NORMAL)  #
    link_entry.insert(0, download_link)  # Adds download_link to entry box
    link_entry.config(state=DISABLED)  #
    save_btn.config(state=NORMAL)
    list_all_formats.config(state=NORMAL)
    try:
        title_name_command = '"' + youtube_dl_cli + ' -s --get-filename -o "%(title)s.%(ext)s" ' + download_link + '"'
        extract_title_name = subprocess.Popen('cmd /c ' + title_name_command, universal_newlines=True,
                                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                              stdin=subprocess.DEVNULL,
                                              creationflags=subprocess.CREATE_NO_WINDOW)
        extract_string = extract_title_name.communicate()[0]
        string_one = resub('[^a-zA-Z0-9 \n\.]', '', extract_string)
        string_two = " ".join(string_one.split())
        extracted_title_name = pathlib.Path(string_two[:128]).with_suffix('')
    except:
        extracted_title_name = download_link
    link_input_label.configure(text=extracted_title_name)

# ------------------------------------------------------------------------------------------------------------ Add Link

# File Output ---------------------------------------------------------------------------------------------------------
def file_save():
    global VideoOutput
    save_entry.config(state=NORMAL)  #
    save_entry.delete(0, END)  # This function clears entry box in order to add new link to entry box
    save_entry.config(state=DISABLED)  #
    VideoOutput = filedialog.askdirectory(parent=main)  # Pop up window to choose a save directory location
    if VideoOutput:
        save_for_entry = '"' + VideoOutput + '/"'  # Completes save directory and adds quotes
        save_entry.config(state=NORMAL)  #
        save_entry.insert(0, save_for_entry)  # Adds download_link to entry box
        save_entry.config(state=DISABLED)  #
        command_line_btn.config(state=NORMAL)  # Enables Button
        start_job_btn.config(state=NORMAL)  # Enalbes Button

# --------------------------------------------------------------------------------------------------------- File Output

# Audio Only Function -------------------------------------------------------------------------------------------------
def set_video_only():
    global audio_format_selection, audio_quality_selection
    if video_only.get() == 'on':
        metadata_from_title_checkbox.config(state=NORMAL)
        metadata_from_title.set('')
        metadata_from_title_checkbox.config(state=DISABLED)
        audio_format_menu.config(state=NORMAL)
        audio_format.set('WAV')
        audio_format_menu.config(state=DISABLED)
        highest_quality_audio_only_checkbox.config(state=NORMAL)
        highest_quality_audio_only.set('')
        highest_quality_audio_only_checkbox.config(state=DISABLED)
        audio_quality_menu.config(state=NORMAL)
        audio_quality.set('5 - Default')
        audio_quality_menu.config(state=DISABLED)
        tabs.tab(2, state=DISABLED)
    elif video_only.get() != 'on':
        metadata_from_title_checkbox.config(state=NORMAL)
        metadata_from_title.set('')
        audio_format_menu.config(state=NORMAL)
        audio_format.set('WAV')
        highest_quality_audio_only_checkbox.config(state=NORMAL)
        highest_quality_audio_only.set('')
        audio_quality_menu.config(state=NORMAL)
        audio_quality.set('5 - Default')
        tabs.tab(2, state=NORMAL)

# ------------------------------------------------------------------------------------------------- Audio Only Function
def highest_quality_audio_only_toggle():
    if highest_quality_audio_only.get() == 'on':
        audio_format.set('WAV')
        audio_format_menu.config(state=DISABLED)
        audio_quality.set('5 - Default')
        audio_quality_menu.config(state=DISABLED)
    if highest_quality_audio_only.get() != 'on':
        audio_format_menu.config(state=NORMAL)
        audio_format.set('WAV')
        audio_quality_menu.config(state=NORMAL)
        audio_quality.set('5 - Default')

# Video Only Checkbutton ----------------------------------------------------------------------------------------------
video_only = StringVar()
video_only_checkbox = Checkbutton(video_frame, text='Best Video + Audio\nSingle File', variable=video_only,
                                  onvalue='on', offvalue='', command=set_video_only, takefocus=False)
video_only_checkbox.grid(row=0, column=0, columnspan=1, rowspan=1, padx=10, pady=6, sticky=N + S + E + W)
video_only_checkbox.configure(background="#434547", foreground="white", activebackground="#434547",
                              activeforeground="white", selectcolor="#434547", font=("Helvetica", 12))
video_only.set('')

# ---------------------------------------------------------------------------------------------- Video Only Checkbutton

# Highest Quality Audio Only ------------------------------------------------------------------------------------------
highest_quality_audio_only = StringVar()
highest_quality_audio_only_checkbox = Checkbutton(audio_frame, text='Extract Audio Only\nNo Encode',
                                                  variable=highest_quality_audio_only, onvalue='on', offvalue='',
                                                  command=highest_quality_audio_only_toggle, takefocus=False)
highest_quality_audio_only_checkbox.grid(row=0, column=0, columnspan=1, rowspan=1, padx=10, pady=3,
                                         sticky=N + S + E + W)
highest_quality_audio_only_checkbox.configure(background="#434547", foreground="white", activebackground="#434547",
                                              activeforeground="white", selectcolor="#434547",
                                              font=("Helvetica", 12))
highest_quality_audio_only.set("on")

# ------------------------------------------------------------------------------------------ Highest Quality Audio Only

# Add Meta-Data From Title --------------------------------------------------------------------------------------------
metadata_from_title = StringVar()
metadata_from_title_checkbox = Checkbutton(audio_frame, text='Add Meta-Data\nFrom Title',
                                           variable=metadata_from_title,
                                           onvalue='--add-metadata --metadata-from-title "%(artist)s" ',
                                           offvalue='',
                                           takefocus=False)
metadata_from_title_checkbox.grid(row=1, column=0, columnspan=1, rowspan=1, padx=10, pady=3, sticky=N + S + E + W)
metadata_from_title_checkbox.configure(background="#434547", foreground="white", activebackground="#434547",
                                       activeforeground="white", selectcolor="#434547", font=("Helvetica", 12))
metadata_from_title.set('')

# -------------------------------------------------------------------------------------------- Add Meta-Data From Title

# Audio Format Selection ----------------------------------------------------------------------------------------------
def audio_format_menu_hover(e):
    audio_format_menu["bg"] = "grey"
    audio_format_menu["activebackground"] = "grey"

def audio_format_menu_hover_leave(e):
    audio_format_menu["bg"] = "#23272A"

audio_format = StringVar(main)
audio_format_choices = {'WAV': '--audio-format wav ',
                        'AAC': '--audio-format aac ',
                        'FLAC': '--audio-format flac ',
                        'MP3': '--audio-format mp3 ',
                        'M4A': '--audio-format m4a ',
                        'Opus': '--audio-format opus ',
                        'Vorbis': '--audio-format vorbis '}
audio_format_menu_label = Label(audio_frame, text="Audio Format :", background="#434547",
                                foreground="white")
audio_format_menu_label.grid(row=0, column=1, columnspan=2, padx=10, pady=(3, 10), sticky=W + E)
audio_format_menu = OptionMenu(audio_frame, audio_format, *audio_format_choices.keys())
audio_format_menu.config(background="#23272A", foreground="white", highlightthickness=1, width=19, state=DISABLED)
audio_format_menu.grid(row=1, column=1, columnspan=2, padx=10, pady=(3, 10))
audio_format.set('WAV')
audio_format_menu["menu"].configure(activebackground="dim grey")
audio_format_menu.bind("<Enter>", audio_format_menu_hover)
audio_format_menu.bind("<Leave>", audio_format_menu_hover_leave)

# -------------------------------------------------------------------------------------------------------- Audio Format

# Download Rate -------------------------------------------------------------------------------------------------------
def download_rate_menu_hover(e):
    download_rate_menu["bg"] = "grey"
    download_rate_menu["activebackground"] = "grey"

def download_rate_menu_hover_leave(e):
    download_rate_menu["bg"] = "#23272A"

download_rate = StringVar(main)
download_rate_choices = {'Unlimited': '',
                         '10 - KiB      (Slowest)': '-r 10K ',
                         '50 - KiB': '-r 50K ',
                         '100 - KiB': '-r 100K ',
                         '250 - KiB': '-r 250K ',
                         '500 - KiB': '-r 500K ',
                         '750 - KiB': '-r 750K ',
                         '1 - MiB': '-r 1M ',
                         '5 - MiB': '-r 5M ',
                         '10 - MiB': '-r 10M ',
                         '30 - MiB': '-r 30M ',
                         '50 - MiB': '-r 50M ',
                         '100 - MiB': '-r 100M ',
                         '500 - MiB': '-r 500M ',
                         '1000 - MiB  (Fastest)': '-r 1000M '}
download_rate_menu_label = Label(general_frame, text="Download Rate :", background="#434547",
                                 foreground="white")
download_rate_menu_label.grid(row=0, column=0, columnspan=1, padx=10, pady=(3, 10), sticky=W + E)
download_rate_menu = OptionMenu(general_frame, download_rate, *download_rate_choices.keys())
download_rate_menu.config(background="#23272A", foreground="white", highlightthickness=1, width=19)
download_rate_menu.grid(row=1, column=0, columnspan=1, padx=10, pady=(3, 10))
download_rate.set('Unlimited')
download_rate_menu["menu"].configure(activebackground="dim grey")
download_rate_menu.bind("<Enter>", download_rate_menu_hover)
download_rate_menu.bind("<Leave>", download_rate_menu_hover_leave)
# ------------------------------------------------------------------------------------------------------- Download Rate

# No Continue Checkbutton ---------------------------------------------------------------------------------------------
no_continue = StringVar()
no_continue_checkbox = Checkbutton(general_frame, text='Resume\nDownload', variable=no_continue,
                                   onvalue='', offvalue='--no-continue ', takefocus=False)
no_continue_checkbox.grid(row=0, column=1, columnspan=1, rowspan=1, padx=10, pady=3, sticky=N + S + E + W)
no_continue_checkbox.configure(background="#434547", foreground="white", activebackground="#434547",
                               activeforeground="white", selectcolor="#434547", font=("Helvetica", 12))
no_continue.set('')

# --------------------------------------------------------------------------------------------------------- No Continue

# No Part Checkbutton -------------------------------------------------------------------------------------------------
no_part = StringVar()
no_part_checkbox = Checkbutton(general_frame, text="Don't Use\n.part Files", variable=no_part,
                               onvalue='--no-part ', offvalue='', takefocus=False)
no_part_checkbox.grid(row=0, column=2, columnspan=1, rowspan=1, padx=10, pady=3, sticky=N + S + E + W)
no_part_checkbox.configure(background="#434547", foreground="white", activebackground="#434547",
                           activeforeground="white", selectcolor="#434547", font=("Helvetica", 12))
no_part.set('')

# ------------------------------------------------------------------------------------------------------------- No Part

# Youtube-Subtitle Checkbutton ----------------------------------------------------------------------------------------
yt_subtitle = StringVar()
yt_subtitle_checkbox = Checkbutton(general_frame, text="Auto Write Subs\n(Youtube Only / If Aval)",
                                   variable=yt_subtitle, onvalue='--write-auto-sub ', offvalue='', takefocus=False)
yt_subtitle_checkbox.grid(row=1, column=1, columnspan=1, rowspan=1, padx=10, pady=3, sticky=N + S + E + W)
yt_subtitle_checkbox.configure(background="#434547", foreground="white", activebackground="#434547",
                               activeforeground="white", selectcolor="#434547", font=("Helvetica", 12))
yt_subtitle.set('')

# ---------------------------------------------------------------------------------------------------- Youtube Subtitle

# dl_playlist Checkbutton ---------------------------------------------------------------------------------------------
dl_playlist = StringVar()
dl_playlist_checkbox = Checkbutton(general_frame, text="Only Download Single\nFile From Playlist",
                                   variable=dl_playlist, onvalue='--no-playlist', offvalue='--yes-playlist',
                                   takefocus=False)
dl_playlist_checkbox.grid(row=1, column=2, columnspan=1, rowspan=1, padx=10, pady=3, sticky=N + S + E + W)
dl_playlist_checkbox.configure(background="#434547", foreground="white", activebackground="#434547",
                               activeforeground="white", selectcolor="#434547", font=("Helvetica", 12))
dl_playlist.set('--yes-playlist')

# --------------------------------------------------------------------------------------------------------- dl_playlist

# Skip Unavaliable Checkbutton ----------------------------------------------------------------------------------------
ignore_errors = StringVar()
ignore_errors_checkbox = Checkbutton(general_frame, text="Skip Unavailable\nVideos",
                                     variable=ignore_errors, onvalue='-i', offvalue='',
                                     takefocus=False)
ignore_errors_checkbox.grid(row=2, column=2, columnspan=1, rowspan=1, padx=10, pady=3, sticky=N + S + E + W)
ignore_errors_checkbox.configure(background="#434547", foreground="white", activebackground="#434547",
                                 activeforeground="white", selectcolor="#434547", font=("Helvetica", 12))
ignore_errors.set('-i')

# ---------------------------------------------------------------------------------------- Skip Unavaliable Checkbutton

# Audio Quality Selection ---------------------------------------------------------------------------------------------
def audio_quality_menu_hover(e):
    audio_quality_menu["bg"] = "grey"
    audio_quality_menu["activebackground"] = "grey"

def audio_quality_menu_hover_leave(e):
    audio_quality_menu["bg"] = "#23272A"

audio_quality = StringVar(main)
audio_quality_choices = {'0 - Best': '--audio-quality 0 -x ',
                         '1': '--audio-quality 1 -x ',
                         '2': '--audio-quality 2 -x ',
                         '3': '--audio-quality 3 -x ',
                         '4': '--audio-quality 4 -x ',
                         '5 - Default': '--audio-quality 5 -x ',
                         '6': '--audio-quality 6 -x ',
                         '7': '--audio-quality 7 -x ',
                         '8': '--audio-quality 8 -x ',
                         '9 - Worse': '--audio-quality 9 -x '}
audio_quality_menu_label = Label(audio_frame, text="Audio Quality (VBR) :", background="#434547",
                                 foreground="white")
audio_quality_menu_label.grid(row=0, column=3, columnspan=2, padx=10, pady=(3, 10), sticky=W + E)
audio_quality_menu = OptionMenu(audio_frame, audio_quality, *audio_quality_choices.keys())
audio_quality_menu.config(background="#23272A", foreground="white", highlightthickness=1, width=19, state=DISABLED)
audio_quality_menu.grid(row=1, column=3, columnspan=2, padx=10, pady=(3, 10))
audio_quality.set('5 - Default')
audio_quality_menu["menu"].configure(activebackground="dim grey")
audio_quality_menu.bind("<Enter>", audio_quality_menu_hover)
audio_quality_menu.bind("<Leave>", audio_quality_menu_hover_leave)

# ------------------------------------------------------------------------------------------------------- Audio Quality

# Views Command -------------------------------------------------------------------------------------------------------
def view_command():
    global cmd_line_window
    global cmd_label
    if video_only.get() != 'on':
        if highest_quality_audio_only.get() == 'on':
            audio_format_selection = '--audio-format best -x '
            audio_quality_selection = ''
        elif highest_quality_audio_only.get() != 'on':
            audio_format_selection = audio_format_choices[audio_format.get()]
            audio_quality_selection = audio_quality_choices[audio_quality.get()]
    elif video_only.get() == 'on':
        audio_format_selection = ''
        audio_quality_selection = ''
    example_cmd_output = '--console-title ' \
                         + audio_format_selection + audio_quality_selection \
                         + download_rate_choices[download_rate.get()] + no_continue.get() + no_part.get() \
                         + yt_subtitle.get() + metadata_from_title.get() + dl_playlist.get() + ' ' \
                         + ignore_errors.get() + ' -o ' + '"' + '\n\n' + VideoOutput + '/%(title)s.%(ext)s' \
                         + '" ' + '\n\n' + download_link

    try:
        cmd_label.config(text=example_cmd_output)
        cmd_line_window.deiconify()
    except (AttributeError, NameError):
        cmd_line_window = Toplevel()
        cmd_line_window.title('Command Line')
        cmd_line_window.configure(background="#434547")
        cmd_label = Label(cmd_line_window, text=example_cmd_output, foreground="white",
                          background="#434547")
        cmd_label.config(font=("Helvetica", 16))
        cmd_label.pack()

        def hide_instead():
            cmd_line_window.withdraw()

        cmd_line_window.protocol('WM_DELETE_WINDOW', hide_instead)

# ------------------------------------------------------------------------------------------------------- Views Command

# Start Job -----------------------------------------------------------------------------------------------------------
def start_job():
    global custom_job, output_name, audio_textinput, video_textinput, stream_window, extracted_title_name
    if shell_options.get() == 'Default':  # This allows the program to spawn new windows and provide real time progress
        def close_encode():
            confirm_exit = messagebox.askyesno(title='Prompt',
                                               message="Are you sure you want to stop progress?", parent=window)
            if confirm_exit == False:
                pass
            elif confirm_exit == True:
                subprocess.Popen(f"TASKKILL /F /PID {job.pid} /T", creationflags=subprocess.CREATE_NO_WINDOW)
                window.destroy()

        def close_window():
            thread = threading.Thread(target=close_encode)
            thread.start()

    if custom_job == 'On':  # Code required for custom job selection
        def custom_file_save_location():
            global output_name
            output_name = filedialog.asksaveasfilename(parent=stream_window, title='Save File Name', initialdir='/',
                                                       initialfile=extracted_title_name, defaultextension='')

        vid_text_input = video_textinput.get('1.0', 'end-1c').replace(' ', '')
        aud_text_input = audio_textinput.get('1.0', 'end-1c').replace(' ', '')

        if len(vid_text_input) == 0 and len(aud_text_input) == 0:
            messagebox.showinfo(title='Info', message='Please type in an ID code for desired output',
                                parent=stream_window)
        if len(vid_text_input) > 0 and len(aud_text_input) == 0:
            custom_code_input = vid_text_input
            custom_file_save_location()
        if len(vid_text_input) == 0 and len(aud_text_input) > 0:
            custom_code_input = aud_text_input
            custom_file_save_location()
        if len(vid_text_input) > 0 and len(aud_text_input) > 0:
            custom_code_input = vid_text_input + '+' + aud_text_input
            custom_file_save_location()

        command = '"' + youtube_dl_cli + ' --ffmpeg-location ' + ffmpeg + ' --console-title ' \
                  + '--no-playlist ' + '-o ' + '"' + output_name + '.mkv" ' + '-f ' + custom_code_input + ' ' \
                  + '--merge-output-format mkv "' + download_link + '""'

        if shell_options.get() == "Default" and output_name == '':
            pass
        if shell_options.get() == "Default" and output_name != '':
            if config['close_custom_window_auto']['option'] == 'on':
                stream_window.destroy()
            window = Toplevel(main)
            window.title(download_link)
            window.configure(background="#434547")
            encode_label = Label(window, text='- ' * 22 + 'Progress ' + '- ' * 22,
                                 font=("Times New Roman", 14), background='#434547', foreground="white")
            encode_label.grid(column=0, columnspan=2, row=0)
            window.grid_columnconfigure(0, weight=1)
            window.grid_rowconfigure(0, weight=1)
            window.grid_rowconfigure(1, weight=1)
            window.protocol('WM_DELETE_WINDOW', close_window)
            window.geometry("600x140")
            encode_window_progress = Text(window, height=2, relief=SUNKEN, bd=3)
            encode_window_progress.grid(row=1, column=0, columnspan=2, pady=(10, 6), padx=10, sticky=E + W)
            encode_window_progress.insert(END, '')
            app_progress_bar = ttk.Progressbar(window, orient=HORIZONTAL, mode='determinate')
            app_progress_bar.grid(row=2, columnspan=2, pady=(10, 10), padx=15, sticky=E + W)

            job = subprocess.Popen('cmd /c ' + command, universal_newlines=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
            for line in job.stdout:
                encode_window_progress.delete('1.0', END)
                encode_window_progress.insert(END, line)
                try:
                    download = line.split()[1].rsplit('.', 1)[0]
                    app_progress_bar['value'] = int(download)
                except:
                    pass
            window.destroy()
        elif shell_options.get() == 'Debug' and output_name == '':
            pass
        elif shell_options.get() == 'Debug' and output_name != '':
            if config['close_custom_window_auto']['option'] == 'on':
                stream_window.destroy()
            subprocess.Popen('cmd /k' + command)
        try:
            cmd_line_window.withdraw()
        except:
            pass

    if custom_job == 'Off':  # All jobs that aren't part of the custom job window
        if video_only.get() != 'on':
            if highest_quality_audio_only.get() == 'on':
                audio_format_selection = '--audio-format best -x '
                audio_quality_selection = ''
            elif highest_quality_audio_only.get() != 'on':
                audio_format_selection = audio_format_choices[audio_format.get()]
                audio_quality_selection = audio_quality_choices[audio_quality.get()]
        elif video_only.get() == 'on':
            audio_format_selection = ''
            audio_quality_selection = ''
        command = '"' + youtube_dl_cli + ' --ffmpeg-location ' + ffmpeg + ' --console-title ' \
                  + audio_format_selection + audio_quality_selection + metadata_from_title.get() \
                  + download_rate_choices[download_rate.get()] + no_continue.get() + no_part.get() \
                  + yt_subtitle.get() + dl_playlist.get() + ' ' + ignore_errors.get() \
                  + ' -o ' + '"' + VideoOutput + '/%(title)s.%(ext)s' + '" "' + download_link + '""'
        if shell_options.get() == "Default":
            window = Toplevel(main)
            window.title(download_link)
            window.configure(background="#434547")
            encode_label = Label(window, text='- ' * 22 + 'Progress ' + '- ' * 22,
                                 font=("Times New Roman", 14), background='#434547', foreground="white")
            encode_label.grid(column=0, columnspan=2, row=0)
            window.grid_columnconfigure(0, weight=1)
            window.grid_rowconfigure(0, weight=1)
            window.grid_rowconfigure(1, weight=1)
            window.protocol('WM_DELETE_WINDOW', close_window)
            window.geometry("600x140")
            encode_window_progress = Text(window, height=2, relief=SUNKEN, bd=3)
            encode_window_progress.grid(row=1, column=0, columnspan=2, pady=(10, 6), padx=10, sticky=E + W)
            encode_window_progress.insert(END, '')
            app_progress_bar = ttk.Progressbar(window, orient=HORIZONTAL, mode='determinate')
            app_progress_bar.grid(row=2, columnspan=2, pady=(10, 10), padx=15, sticky=E + W)

            job = subprocess.Popen('cmd /c ' + command, universal_newlines=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
            for line in job.stdout:
                encode_window_progress.delete('1.0', END)
                encode_window_progress.insert(END, line)
                try:
                    download = line.split()[1].rsplit('.', 1)[0]
                    app_progress_bar['value'] = int(download)
                except:
                    pass
                try:  # Block of code to make a new mini progress bar if the user is downloading a playlist
                    playlist_amnt = line.split()[0]
                    if playlist_amnt == '[download]':
                        amount = line.split()[2]
                        if amount == 'video':
                            window.geometry("600x190")
                            modify_line = line.split()[1:]
                            total_file_progress = (', '.join(modify_line).replace(',', '').replace('video', 'file'))
                            progress_label = Label(window, text=total_file_progress, font=("Times New Roman", 14),
                                                   background='#434547', foreground="white")
                            progress_label.grid(row=3, column=0, pady=(0, 20))
                            file_progress = line.split()[3]
                            file_progress_total = line.split()[5]
                            mini_progressbar = ttk.Progressbar(window, orient=HORIZONTAL, length=300,
                                                               mode='determinate')
                            mini_progressbar.grid(row=3, column=1, pady=(0, 10), padx=(0, 15))
                            percent = '{:.1%}'.format(int(file_progress) / int(file_progress_total)).split('.', 1)[0]
                            mini_progressbar['value'] = int(percent)
                except:
                    pass
            window.destroy()
        elif shell_options.get() == 'Debug':
            subprocess.Popen('cmd /k' + command)
        try:
            cmd_line_window.withdraw()
        except:
            pass

# ----------------------------------------------------------------------------------------------------------- Start Job

# Buttons and Entry Box's ---------------------------------------------------------------------------------------------
text_area = scrolledtext.ScrolledText(link_frame, wrap=WORD, width=69, height=1, font=("Times New Roman", 14),
                                      foreground="grey")
text_area.insert(END, "Right Click or 'Ctrl + V'")
text_area.grid(row=0, column=0, columnspan=3, pady=(1, 5), padx=10, sticky=W + E)

# -------------------------------------------------------------------------- Right click menu to paste in text_area box
def paste_clipboard():  # Allows user to paste what ever is in their clipboard with right click and paste
    text_area.delete(1.0, END)
    text_area.config(foreground="black")
    text_area.insert(END, pyperclip.paste())

def remove_text(e):  # Deletes current text in text box upon 'Left Clicking'
    text_area.config(foreground="black")
    text_area.delete(1.0, END)
    link_input_label.configure(text='Please Paste Link Above and Select "Add Link"')
    link_entry.config(state=NORMAL)  #
    link_entry.delete(0, END)  # This function clears entry box in order to add new link to entry box
    link_entry.config(state=DISABLED)  #

m = Menu(main, tearoff=0)  # Pop up menu for 'Paste'
m.add_command(label="Paste", command=paste_clipboard)

def do_popup(event):
    try:
        m.tk_popup(event.x_root, event.y_root)
    finally:
        m.grab_release()

text_area.bind("<Button-3>", do_popup)  # Uses right click to make a function
text_area.bind("<Button-1>", remove_text)  # Uses left click to make a function
# Right click menu to paste in text_area box --------------------------------------------------------------------------

link_entry = Entry(link_frame, borderwidth=4, background="#CACACA", state=DISABLED, width=70)
link_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=(0, 0), sticky=W + E)

def apply_btn_hover(e):
    apply_btn["bg"] = "grey"

def apply_btn_hover_leave(e):
    apply_btn["bg"] = "#8b0000"

apply_btn = Button(link_frame, text="Add Link", command=apply_link, foreground="white", background="#8b0000",
                   width=30)
apply_btn.grid(row=1, column=0, columnspan=1, padx=10, pady=5, sticky=W)
apply_btn.bind("<Enter>", apply_btn_hover)
apply_btn.bind("<Leave>", apply_btn_hover_leave)

def save_btn_hover(e):
    save_btn["bg"] = "grey"

def save_btn_hover_leave(e):
    save_btn["bg"] = "#8b0000"

save_btn = Button(main, text="Save Directory", command=file_save, foreground="white", background="#8b0000",
                  state=DISABLED)
save_btn.grid(row=4, column=0, columnspan=1, padx=10, pady=(15, 0), sticky=W + E)
save_btn.bind("<Enter>", save_btn_hover)
save_btn.bind("<Leave>", save_btn_hover_leave)

save_entry = Entry(main, borderwidth=4, background="#CACACA", state=DISABLED)
save_entry.grid(row=4, column=1, columnspan=3, padx=10, pady=(15, 0), sticky=W + E)

def start_job_btn_hover(e):
    start_job_btn["bg"] = "grey"

def start_job_btn_hover_leave(e):
    start_job_btn["bg"] = "#8b0000"

def normal_job_start():  # Sets the custom_job variable and starts the job process
    global custom_job
    custom_job = 'Off'
    threading.Thread(target=start_job).start()

start_job_btn = Button(main, text="Start Job", command=normal_job_start,
                       foreground="white", background="#8b0000", state=DISABLED)
start_job_btn.grid(row=5, column=3, columnspan=1, padx=10, pady=(15, 15), sticky=N + S + W + E)
start_job_btn.bind("<Enter>", start_job_btn_hover)
start_job_btn.bind("<Leave>", start_job_btn_hover_leave)

def command_line_btn_hover(e):
    command_line_btn["bg"] = "grey"

def command_line_btn_hover_leave(e):
    command_line_btn["bg"] = "#8b0000"

command_line_btn = Button(main, text="View Command", command=view_command, foreground="white", background="#8b0000",
                          state=DISABLED)
command_line_btn.grid(row=5, column=0, columnspan=1, padx=10, pady=(15, 15), sticky=N + S + W + E)
command_line_btn.bind("<Enter>", command_line_btn_hover)
command_line_btn.bind("<Leave>", command_line_btn_hover_leave)

def list_all_formats_hover(e):
    list_all_formats["bg"] = "grey"

def list_all_formats_hover_leave(e):
    list_all_formats["bg"] = "#8b0000"

# Function and GUI button to 'Show All Formats' -----------------------------------------------------------------------
def custom_format():
    global download_link, stream_window, audio_textinput, video_textinput, vidtest, extracted_title_name, \
        auto_close_custom
    try:
        command = '"' + youtube_dl_cli + ' -F ' + download_link + '"'
        run = subprocess.Popen('cmd /c ' + command, creationflags=subprocess.CREATE_NO_WINDOW,
                               universal_newlines=True,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
        try:
            stream_window.destroy()
        except:
            pass
        stream_window = Toplevel()
        stream_window.title('Custom Download Options')
        stream_window.configure(background="#434547")
        show_format_text = scrolledtext.ScrolledText(stream_window, width=120, height=25, tabs=10)
        show_format_text.grid(column=0, pady=10, padx=10, row=0, columnspan=3)
        show_format_text.configure(state=NORMAL)
        show_format_text.insert(END, '- - - - - Match the format code on the left '
                                     'in the video/audio boxes for desired outcome - - - - -\n\n\n'
                                + str(extracted_title_name) + '\n\n', 'centered')
        show_format_text.tag_configure("centered", justify="center", font=("Times New Roman", 16))

        def set_auto_close_custom():
            config.set('close_custom_window_auto', 'option', auto_close_custom.get())
            try:
                with open(config_file, 'w') as configfile:
                    config.write(configfile)
            except:
                pass

        auto_close_custom = StringVar()
        auto_close_custom_checkbox = Checkbutton(stream_window, text='Close Automatically',
                                                 variable=auto_close_custom, onvalue='on', offvalue='off',
                                                 command=set_auto_close_custom, takefocus=False)
        auto_close_custom_checkbox.grid(row=2, column=0, columnspan=1, rowspan=2, padx=10, pady=6, sticky=W)
        auto_close_custom_checkbox.configure(background="#434547", foreground="white", activebackground="#434547",
                                      activeforeground="white", selectcolor="#434547", font=("Helvetica", 12))
        auto_close_custom.set(config['close_custom_window_auto']['option'])
        v_label = Label(stream_window, text='Video ID:' + ' ' * 17, background='#434547', foreground="white")
        v_label.grid(column=1, row=2, columnspan=1, padx=10, pady=3, sticky=E)
        a_label = Label(stream_window, text='Audio ID:', background='#434547', foreground="white")
        a_label.grid(column=2, row=2, columnspan=1, padx=10, pady=3, sticky=W)
        video_textinput = Text(stream_window, height=1, width=14)
        video_textinput.grid(row=3, column=1, columnspan=1, padx=10, pady=3, sticky=E)
        audio_textinput = Text(stream_window, height=1, width=14)
        audio_textinput.grid(row=3, column=2, columnspan=1, padx=10, pady=3, sticky=W)

        def start_audio_job_custom():
            global custom_job, output_name
            custom_job = 'On'
            threading.Thread(target=start_job).start()

        start_custom_button = Button(stream_window, text="Start Audio Job",
                                     command=start_audio_job_custom, foreground="white", background="#8b0000",
                                     borderwidth="3")
        start_custom_button.grid(row=3, column=2, columnspan=3, padx=10, pady=5, sticky=E)

        def start_custom_button_hover(e):
            start_custom_button["bg"] = "grey"

        def start_custom_button_hover_leave(e):
            start_custom_button["bg"] = "#8b0000"

        start_custom_button.bind("<Enter>", start_custom_button_hover)
        start_custom_button.bind("<Leave>", start_custom_button_hover_leave)
        for line in run.stdout:
            show_format_text.insert(END, line)
            show_format_text.insert(END, '-------------------------' * 6 + '\n', 'boldfont')
            show_format_text.tag_configure("boldfont", font=("ArialBlack"))
        show_format_text.configure(state=DISABLED)
    except NameError:
        messagebox.showerror(title='Error', message='Please Paste a Video Link First')

# -------------------------------------------------------------------------------------------------------- Show Formats

list_all_formats = Button(main, text="Custom Download",
                          command=lambda: threading.Thread(target=custom_format).start(),
                          foreground="white", background="#8b0000", state=DISABLED)
list_all_formats.grid(row=5, column=1, columnspan=2, padx=10, pady=(15, 15), sticky=N + S + W + E)
list_all_formats.bind("<Enter>", list_all_formats_hover)
list_all_formats.bind("<Leave>", list_all_formats_hover_leave)

# --------------------------------------------------------------------------------------------- Buttons and Entry Box's

# Checks config for bundled app paths path ---------------
def check_ffmpeg():
    global ffmpeg
    # FFMPEG --------------------------------------------------------------
    if shutil.which('ffmpeg') != None:
        ffmpeg = '"' + str(pathlib.Path(shutil.which('ffmpeg'))).lower() + '"'
        messagebox.showinfo(title='Prompt!', message='ffmpeg.exe found on system PATH, '
                                                     'automatically setting path to location.\n\n'
                                                     'Note: This can be changed in the config.ini file'
                                                     ' or in the Options menu')
        if pathlib.Path("Apps/ffmpeg/ffmpeg.exe").exists():
            rem_ffmpeg = messagebox.askyesno(title='Delete Included ffmpeg?',
                                             message='Would you like to delete the included FFMPEG?')
            if rem_ffmpeg == True:
                try:
                    shutil.rmtree(str(pathlib.Path("Apps/ffmpeg")))
                except:
                    pass
        config.set('ffmpeg_path', 'path', ffmpeg)
        with open(config_file, 'w') as configfile:
            config.write(configfile)
    elif pathlib.Path("Apps/ffmpeg/ffmpeg.exe").exists():
        messagebox.showinfo(title='Info', message='Program will use the included '
                                                  '"ffmpeg.exe" located in the "Apps" folder')
        ffmpeg = '"' + str(pathlib.Path("Apps/ffmpeg/ffmpeg.exe")) + '"'
    try:
        config.set('ffmpeg_path', 'path', ffmpeg)
        with open(config_file, 'w') as configfile:
            config.write(configfile)
    except:
        pass
    # FFMPEG ------------------------------------------------------------------

def check_youtubedl():
    global youtube_dl_cli
    # youtubeDL cli -------------------------------------------------------------
    if youtube_dl_cli == '' or not pathlib.Path(youtube_dl_cli.replace('"', '')).exists():
        youtube_dl_cli = '"' + str(pathlib.Path('Apps/yt-dlp/yt-dlp.exe')) + '"'
        try:
            config.set('youtubedl_path', 'path', youtube_dl_cli)
            with open(config_file, 'w') as configfile:
                config.write(configfile)
        except:
            pass
    # youtubeDL cli ----------------------------------------------------------

if config['ffmpeg_path']['path'] == '' or not pathlib.Path(ffmpeg.replace('"', '')).exists():
    check_ffmpeg()
if config['youtubedl_path']['path'] == '' or not pathlib.Path(youtube_dl_cli.replace('"', '')).exists():
    check_youtubedl()

# Checks if needed executables are found by the program -----------------------------------------
def downloadfiles():
    def open_window():
        global window_message

        def dw_exit_function():
            confirm_exit = messagebox.askyesno(title='Prompt',
                                               message="Are you sure you want to exit the program?\n"
                                                       "\nYou could potentially corrupt some required"
                                                       " applications\n\nIf this happens delete the "
                                                       "'Apps' folder and restart the program",
                                               parent=main)
            if confirm_exit == False:
                pass
            elif confirm_exit == True:
                main.destroy()

        window_message = Toplevel(master=main)
        window_message.title('Download')
        window_message.configure(background="#434547")
        window_height = 80
        window_width = 340
        screen_width = window_message.winfo_screenwidth()
        screen_height = window_message.winfo_screenheight()
        x_coordinate = int((screen_width / 2) - (window_width / 2))
        y_coordinate = int((screen_height / 2) - (window_height / 2))
        window_message.geometry(
            f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")  # Window for download
        window_message.protocol('WM_DELETE_WINDOW', dw_exit_function)
        window_message.transient(main)
        window_message.grab_set()

    download_links_config = 'Runtime/downloadlinks.ini'  # Creates (if doesn't exist) and defines location of config.ini
    dl_link_parser = ConfigParser()
    dl_link_parser.read(download_links_config)

    # FFMPEG check -------------------------------------------------------------------
    if not pathlib.Path(config['ffmpeg_path']['path'].replace('"', '')).is_file():
        ffmpeg_error = messagebox.askyesnocancel(parent=main, title='FFMPEG Not Found',
                                                 message="            Navigate to 'ffmpeg.exe'\n\n"
                                                         "If you do not have it select 'No' to download")
        if ffmpeg_error == False:  # If ffmpeg_error msgbox 'No' is selected
            open_window()
            lbl = Label(window_message, text='Downloading ffmpeg.7z', bg='#434547', fg='white', font=(None, 18))
            lbl.pack(expand=True, fill='x', padx=10)  # Download window label
            app_progress_bar = ttk.Progressbar(window_message, orient=HORIZONTAL, mode='determinate', )
            app_progress_bar.pack(fill='x', expand=True, padx=10)  # spawns progress bar

            def Download_Progress(block_num, block_size, total_size):
                progress = int((block_num * block_size / total_size) * 100)
                app_progress_bar['value'] = int(progress)  # get download progress and convert it into the visual bar

            pathlib.Path('Apps/temp').mkdir(parents=True, exist_ok=True)  # Makes directory 'temp'
            ssl._create_default_https_context = ssl._create_unverified_context
            urllib.request.urlretrieve(dl_link_parser['ffmpeg_link']['link'], 'Apps/temp/ffmpeg-git-full.7z',
                                       reporthook=Download_Progress)  # Downloads .7z
            sleep(2)  # Halts the program for 2 seconds
            lbl.configure(text='Extracting ffmpeg.exe')  # Update label
            app_progress_bar['value'] = int(0)  # Sets progress bar back to 0%
            sleep(2)  # Halts the program for 2 seconds
            command = '"' + '"Apps/7z/7z.exe" e ' \
                      + '"Apps/temp/ffmpeg-git-full.7z" "-oApps/ffmpeg" ffmpeg.exe -r' + '"'
            subprocess.Popen('cmd /c' + command,
                             creationflags=subprocess.CREATE_NO_WINDOW)  # Command to extract .7z
            app_progress_bar['value'] = int(50)  # Pushes generic percentage to the progressbar
            sleep(1)  # Halts the program for 1 second
            app_progress_bar['value'] = int(100)  # Pushes generic percentage to the progressbar
            lbl.configure(text='Extraction Complete!')  # Updates label
            sleep(1)  # Halts the program for 1 second
            check_ffmpeg()  # Runs the check_ffmpeg to look for ffmpeg/write where it is to the config file
            if pathlib.Path(config['ffmpeg_path']['path'].replace('"', '')).is_file():
                lbl.configure(text=config['ffmpeg_path']['path'])  # Uses the written config 'ffmpeg_path' on label
                sleep(2)  # Halts the program for 2 seconds
                window_message.destroy()  # Closes the download window
            if not pathlib.Path(config['ffmpeg_path']['path'].replace('"', '')).is_file():
                messagebox.showinfo(parent=main, title='Info', message='Could not download file')  # Error
            shutil.rmtree('Apps/temp', ignore_errors=True)
        elif ffmpeg_error == True:  # If user selects 'Yes,' this runs the function to define the path
            set_ffmpeg_path()
        elif ffmpeg_error == None:
            messagebox.showerror(title='Error!', message='Program cannot post process without "ffmpeg.exe"')
            #main.destroy()  # If user selects 'Cancel,' the main program closes

    # -------------------------------------------------------------------- FFMPEG check

    # youtube-dl check ---------------------------------------------------------------------
    if not pathlib.Path(config['youtubedl_path']['path'].replace('"', '')).is_file():
        youtubedl_error = messagebox.askyesnocancel(parent=main, title='yt-dlp Not Found',
                                                    message="                   Navigate to 'yt-dlp.exe'\n\n"
                                                            "If you do not have it select 'No' "
                                                            "to download automatically")
        if youtubedl_error == False:  # If user selects 'No' on messagebox prompt
            open_window()
            lbl = Label(window_message, text='Downloading youtube-dl', bg='#434547', fg='white', font=(None, 18))
            lbl.pack(expand=True, fill='x', padx=10)  # Download window label
            app_progress_bar = ttk.Progressbar(window_message, orient=HORIZONTAL, mode='determinate', )
            app_progress_bar.pack(fill='x', expand=True, padx=10)  # spawns progress bar

            def Download_Progress(block_num, block_size, total_size):
                progress = int((block_num * block_size / total_size) * 100)
                app_progress_bar['value'] = int(progress)  # get download progress and convert it into the visual bar
            try:
                urllib.request.urlretrieve(dl_link_parser['youtubedl_link']['link'], 'Apps/yt-dlp/yt-dlp.exe',
                                           reporthook=Download_Progress)
            except urllib.error.HTTPError:
                messagebox.showinfo(parent=main, title='Info', message='Could Not Download youtube-dl.exe!!')
                main.destroy()  # Tries to download latest youtube-dl from main website

            check_youtubedl()  # Runs the function to write youtube-dl to path if needed again after download
            if pathlib.Path(config['youtubedl_path']['path'].replace('"', '')).is_file():
                lbl.configure(text='Downloaded Completed')
                sleep(2)
                window_message.destroy()
            if not pathlib.Path(config['youtubedl_path']['path'].replace('"', '')).is_file():
                messagebox.showinfo(parent=main, title='Info', message='Could not download file')  # Error

        elif youtubedl_error == True:
            set_youtubedl_path()  # If user selects 'Yes,' this runs the function to define the path
        elif youtubedl_error == None:
            messagebox.showerror(title='Error!', message='Program cannot download without "yt-dlp.exe"')
            main.destroy()  # If user selects 'Cancel,' the main program closes

    main.wm_attributes('-alpha', 1.0)  # Remove transparency at the end of download jobs

if pathlib.Path(ffmpeg.replace('"', '')).exists() and pathlib.Path(youtube_dl_cli.replace('"', '')).exists():
    pass
else:
    main.wm_attributes('-alpha', 0.5)  # Makes main transparent during download jobs
    threading.Thread(target=downloadfiles, daemon=True).start()
# ----------------------------------------------------------------------------- youtube-dl check
# Checks if needed executables are found by the program -----------------------------------------

# End Loop ------------------------------------------------------------------------------------------------------------
main.mainloop()
# ------------------------------------------------------------------------------------------------------------ End Loop