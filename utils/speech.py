import speech_recognition as sr

def suara_ke_teks(audio_file):
    recognizer = sr.Recognizer()
    
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
        
    try: 
        hasil = recognizer.recognize_google(
            audio,
            language="id-ID"
        )
        return hasil
    
    except sr.UnknownValueError:
        return ""
    
    except sr.RequestError:
        return "Koneksi internet bermasalah"