import speech_recognition as sr


if __name__ == '__main__':
    #Program changed to write it into a file instead. For people like me who for some reason have over 50 devices???
    File_Thing = open("audios.txt","w")
    for mic_id, mic_name in enumerate(sr.Microphone.list_microphone_names()):
        File_Thing.write(f'{mic_id}: {mic_name}\n')
    File_Thing.close()