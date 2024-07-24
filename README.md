# AnimeWwise
An easy to use tool to extract audio from some anime games, with the original filenames and paths.

![image](https://github.com/user-attachments/assets/e66048df-4d71-4bda-8201-1c2c67f44de7)

# Usage

1. Get the repo by [downloading it](https://github.com/Escartem/WwiseExtract/archive/refs/heads/master.zip) or cloning it (`git clone https://github.com/Escartem/WwiseExtract`)
> [!NOTE]
> This project uses ffmpeg version *3.4.2* which is the latest under 50MB. But it is also slower, if you want to slightly improve extraction speed, consider updating the ffmpeg binary to a [newer version](https://github.com/BtbN/FFmpeg-Builds/releases)
2. Install dependencies -> `pip install -r requirements.txt`
3. Run the app with `python app.py`
4. Select your input folder containing your `.pck` files, it can be your game audio folder directly (if you decide to use this one, make sure the game is not running)
![image](https://github.com/user-attachments/assets/72cf7983-00d0-4e98-b0d0-8b5547057a56)
> [!TIP] 
> The audio folder can be found in the following locations
> - `Genshin Impact\Genshin Impact Game\GenshinImpact_Data\StreamingAssets\AudioAsset\...`
> - `Star Rail... `
> - `Zenless Zone Zero...`
> - (will add later)
5. Select your hdiff folder if needed
> [!NOTE]
> Diff files are `.hdiff` present in the update patches of the games. If you want to extract an hdiff content, you must have the pck file with the *same name before patch* in the input folder, pck's that do not have a corresponding hdiff file will be extracted normally, when they do have a corresponding hdiff file, *only the hdiff file content is extracted* and not the full pck
6. Select a mapping
> [!WARNING]
> By default, the files extracted from the game don't have names, the mappings are here to help restore the original filenames and paths so it's easier to search, but not all games are supported, not at every version and the mapping does not guarantee to have every file named
7. After that, you can browse the files you loaded, if you messed up and wanna go back, you can select File > Reset to unload everything and go back to the starting screen.
![image](https://github.com/user-attachments/assets/9714b6ab-527a-49d9-ae98-354d1979a2b9)
8. In the `Extract` tab, you will be able to select what audio you want, choosing the output folder and audio format. You can extract everything or extract the files you selected in the `Browse` tab
> [!NOTE]
> The program does not check for existing files in the output folder, it will overwrite them, make sure to check your folder before starting the extraction 
9. Extract your files, and enjoy !

# Why was this made

I know there is already dozens of tools that have the exact same purpose, being to extract audio from games or hoyo games, however, I made this anyway because of one functionality that others don't possess, which is file name recovery using mappings, because extracting is cool but browsing thousands of files with no names is just a pain, every single voiceline is a unique file. And I'm also planning a second unique functionality being a lookup tool, giving the user the ability to see every file inside the game, search the ones he needs and then extract them automatically, instead of having to load files and see what's in them. Stay tuned for that one :3

# Contribute

Feel free to contribute to this project as much as you want, a share would be very appreciated aswell, I'll be glad to know if this helped anyone <3
