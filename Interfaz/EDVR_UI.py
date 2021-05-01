import PySimpleGUI as sg
import ffmpeg
import os
import shutil

#def home():
    
    
    
def home():
    sg.theme('Black')
    #Chequear instalacion EDVR correcta 
    layout = [ [sg.Text('Elige un .mp4 para porcesar')],
          [sg.Input(size=(50,1), key='-OUT-')],
          [sg.Button('Buscar')],
          [sg.Text('Quieres usar predeblur? SI/NO')],
          [sg.Input(key='-IN-')],
          [sg.Button('Comenzar'),sg.Button('Exit')] ]
    window = sg.Window('EDVR UI', layout)
    while True: # Event Loop
        event, values = window.read()
        print(event, values)
        if event in (None, 'Exit'):
            break
        if event == 'Buscar':
            path=sg.popup_get_file('Selecciona un video')
            #Chequear que el archivo es un video compatible con ffmpg 
            window['-OUT-'].update(path)
            
        if event == 'Comenzar':
            predb = values['-IN-']
            path = values['-OUT-']
            frames(path,predb)
            #Tiempo entre partes preguntar predeblur 
    window.close()


def frames(path,predb):
    layout = [[sg.Text('Generando los frames, puede tardar un poco.',key='-TEXT-')],
         [sg.Image('/home/gonzalo/Escritorio/frames.PNG',key='-IMAGE-')],
         [sg.Button("Generar"), sg.Button('Exit')]]
    window = sg.Window('EDVR UI', layout)
    while True: # Event Loop
        event, values = window.read()
        print(event, values)
        if event in ('Exit'):
            break
        if event == 'Generar':
            hacer_frames(path)
            window['-TEXT-'].update('Generando los frames LQ, puede tardar un poco.')
            window['-IMAGE-'].update('/home/gonzalo/Escritorio/LQ.PNG')
            
        
    window.close()
    
def hacer_frames(path): 
    print("Entro")
    if os.path.exists('/home/gonzalo/Escritorio/data'):
        print("existe")
        shutil.rmtree("/home/gonzalo/Escritorio/data")
        
    os.mkdir("/home/gonzalo/Escritorio/data")
    
    try:
        (ffmpeg.input(path)
             .filter('fps', fps=30)
             .output('/home/gonzalo/Escritorio/data/%08d.png', 
                     video_bitrate='5000k',
                     s='720x1280',
                     sws_flags='bilinear',
                     start_number=0)
             .run(capture_stdout=True, capture_stderr=True))
    except ffmpeg.Error as e:
            print('stdout:', e.stdout.decode('utf8'))
            print('stderr:', e.stderr.decode('utf8'))    
            
def hacer_LR():
    scriptM =open('generate_LR_Vimeo90K.m', "r")
    list_of_lines = scriptM.readlines()
    #filepaths = dir('/home/gonzalo/Escritorio/data/*.png');
    list_of_lines[6] = "filepaths = dir('/home/gonzalo/Escritorio/data/*.png');\n"
    #    save_LR_folder = strrep(folder_path,'data','data_matlabLRx4');
    list_of_lines[10] = "    save_LR_folder = strrep(folder_path,'data','data_matlabLRx4');\n"
     
    scriptM =open('generate_LR_Vimeo90K.m', "w")
    scriptM.writelines(list_of_lines)
    scriptM.close()
    
    #eng =matlab.engine.start_matlab()
    #eng.generate_LR(nargout=0)
    #eng.quit()            
    
home()     