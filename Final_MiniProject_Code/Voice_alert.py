from gtts import gTTS
import pygame
import time

def save_audio():
    try:
        text = "You are drowsy. Please take rest"
        text2 = "Don't use Phone while driving"
        language = "en-in"
        tts1 = gTTS(text=text, lang=language, slow=True)
        tts2 = gTTS(text=text2, lang=language, slow=True)
        
        # Save the generated speech to a file
        tts1.save("output1.mp3")
        tts2.save("output2.mp3")
        print("Audio files have been saved successfully.")
    except Exception as e:
        print(f"An error occurred while saving audio: {e}")

def play_audio(cls):
    try:
        pygame.mixer.init()
        if cls == "drowsy":
            pygame.mixer.music.load("output1.mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(1)
        elif cls == "using-phone":
            pygame.mixer.music.load("output2.mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(1)
        else:
            print("Invalid classification.")
    except Exception as e:
        print(f"An error occurred while playing audio: {e}")
    finally:
        pygame.mixer.quit()