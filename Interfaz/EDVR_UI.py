import PySimpleGUI as sg
import ffmpeg
import os
import cv2
import shutil
import vlc
from sys import platform as PLATFORM    
    
    
def home():
    sg.theme('Black')
    layout = [ [sg.Text('Recuerda que solo puede procesar vídeos 720 x 1280 o viceversa')],
          [sg.Text('Elige un vídeo para porcesar')],
          [sg.Input(size=(50,1), key='-OUT-')],
          [sg.Button('Buscar')],
          [sg.Checkbox('¿Quieres usar Predeblur?', key='-IN-')],
          [sg.Button('Comenzar'),sg.Button('Exit')] ]
    window = sg.Window('EDVR UI', layout)
    while True: 
        event, values = window.read()
        print(event, values)
        if event in (None, 'Exit'):
            break
        if event == 'Buscar':
            path=sg.popup_get_file('Selecciona un vídeo')
            window['-OUT-'].update(path)
            
        if event == 'Comenzar':
            predb = values['-IN-']
            path_v = values['-OUT-']
            ejecucion(path_v,predb)
    window.close()


def ejecucion(path_v,predb):
    layout = [[sg.Text('Estos son los valores que vas a usar:',size=(55, 1),key='-TEXT-')],
         [sg.Text(path_v, key='-PATH-')],   
         [sg.Text("Predeblur", key='-TEXT2-'), sg.Text(predb, key='-BOOL-')],        
         [sg.Image(None,key='-IMAGE-')],
         [sg.Button("Generar", key='-GEN-'), sg.Button('Exit')]]
    window = sg.Window('EDVR UI', layout)
    while True: # Event Loop
        event, values = window.read()
        print(event, values)
        if event in (None, 'Exit'):
            break
        if event =='-GEN-':
            window['-PATH-'].update(visible=False)
            window['-TEXT2-'].update(visible=False)
            window['-BOOL-'].update(visible=False)
            window['-GEN-'].update(visible=False)
            window['-TEXT-'].update('Generando los frames, puede tardar un poco.')
            window['-IMAGE-'].update('Estados/frames.PNG')
            window.Refresh()
            vid=cv2.VideoCapture(path_v)
            altura=int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
            ancho=int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
            hacer_frames(path_v, altura, ancho)
            number_frames = len(os.listdir('fotogramas/original/000'))
            window['-TEXT-'].update('Generando los frames LQ, puede tardar un poco.')
            window['-IMAGE-'].update('Estados/LQ.PNG')
            window.Refresh()
            hacer_LR3()
            window['-TEXT-'].update('EDVR esta procesando las imágenes.')
            window['-IMAGE-'].update('Estados/EDVR.PNG')
            window.Refresh()
            #Progressbar 
            ejecutar_EDVR(number_frames, predb, altura, ancho)
            window['-TEXT-'].update('Generando el vídeo a partir de las imágenes.')
            window['-IMAGE-'].update('Estados/video.PNG')
            window.Refresh()
            hacer_video()
            window.extend_layout(window, [[sg.B('Sí')]])
            window['-TEXT-'].update('El proceso ya acabado, ¿Quieres visualizar el vídeo?')
            window['-IMAGE-'].update('Estados/video.PNG')
            window.Refresh()
        if event == 'Sí':
            print("Ver Video")
            reproducir_video()
            
    window.close()
    
def hacer_frames(path_v, altura, ancho): 
    resolucion=str(altura) + 'x' + str(ancho)
    
    if os.path.exists('fotogramas/original/000'):
        shutil.rmtree("fotogramas/original/000")
        
    os.mkdir("fotogramas/original/000")
    
    try:
        (ffmpeg.input(path_v)
              .filter('fps', fps=30)
              .output('fotogramas/original/000/%08d.png', 
                      video_bitrate='5000k',
                      s=resolucion,
                      sws_flags='bilinear',
                      start_number=0)
              .run(capture_stdout=True, capture_stderr=True))
    except ffmpeg.Error as e:
        print('stdout:', e.stdout.decode('utf8'))
        print('stderr:', e.stderr.decode('utf8'))    

        
def hacer_LR3():
    if os.path.exists('fotogramas/lr/000'):
        shutil.rmtree("fotogramas/lr/000")
        
    os.mkdir("fotogramas/lr/000")
    
    hr_image_dir = 'fotogramas/original/000'
    lr_image_dir = 'fotogramas/lr/000'
    
    supported_img_formats = (".bmp", ".dib", ".jpeg", ".jpg", ".jpe", ".jp2",
                             ".png", ".pbm", ".pgm", ".ppm", ".sr", ".ras", ".tif",
                             ".tiff")
    
    for filename in os.listdir(hr_image_dir):
        if not filename.endswith(supported_img_formats):
            continue
    
        hr_img = cv2.imread(os.path.join(hr_image_dir, filename))
    
        hr_img = cv2.GaussianBlur(hr_img, (0, 0), 2, 2)
    
        lr_img_4x = cv2.resize(hr_img, (0, 0), fx=0.25, fy=0.25,
                               interpolation=cv2.INTER_CUBIC)
    
        cv2.imwrite(os.path.join(lr_image_dir, filename), lr_img_4x)        
            

def ejecutar_EDVR(number_frames, predb, altura, ancho):
    if os.path.exists('meta_info_MIO.txt'):
         os.remove('meta_info_MIO.txt') 

    os.mknod('meta_info_MIO.txt') 
    
    meta_info=open('meta_info_MIO.txt','w')
    meta_info.write("000 " + str(number_frames) +" (" + str(ancho) + "," + str(altura) + ",3)\n")
    meta_info.close()
    
    test =open('test_EDVR_L_x4_SR_Mio.yml', "r")
    list_of_lines = test.readlines()
    if predb ==True: 
        list_of_lines[32] = "  with_predeblur: true\n"
        list_of_lines[37] = "  pretrain_network_g: EDVR_L_x4_SRblur_REDS_official-983d7b8e.pth\n"
    elif predb ==False: 
         list_of_lines[32] = "  with_predeblur: false\n"
         list_of_lines[37] = "  pretrain_network_g: EDVR_L_x4_SR_REDS_official-9f5f5039.pth\n"

    test =open('test_EDVR_L_x4_SR_Mio.yml', "w")
    test.writelines(list_of_lines)
    test.close()
    os.environ['MKL_THREADING_LAYER'] = 'GNU'
    os.system('PYTHONPATH=”./:${PYTHONPATH}”')
    os.system('CUDA_VISIBLE_DEVICES=0')
    os.system('python ../basicsr/test.py -opt test_EDVR_L_x4_SR_Mio.yml') 


    
def hacer_video(): 
    if os.path.exists('Resultado/resultado.mp4'):
        os.remove('Resultado/resultado.mp4')
    
    try:
        (ffmpeg.input('../results/EDVR_L_x4_Mio/visualization/REDS4/000/*.png', pattern_type='glob', framerate=30)
            .output('Resultado/resultado.mp4', crf=20, preset='slower', movflags='faststart', pix_fmt='yuv420p')
            .run(capture_stdout=True, capture_stderr=True)
    )
    except ffmpeg.Error as e:
        print('stdout:', e.stdout.decode('utf8'))
        print('stderr:', e.stderr.decode('utf8'))    

def btn(name):  
    return sg.Button(name, size=(6, 1), pad=(1, 1))
    
def reproducir_video():
    layout = [[sg.Button('Cargar')],
              [sg.Image('', size=(300, 170), key='-VID_OUT-')],
              [btn('Play'), btn('Pause'), btn('Stop')],
              [sg.Text('Carga el vídeo para empezar', key='-MESSAGE_AREA-')]]
    
    window = sg.Window('EDVR Player', layout, element_justification='center', finalize=True, resizable=True)
    
    window['-VID_OUT-'].expand(True, True)                
    
    inst = vlc.Instance()
    list_player = inst.media_list_player_new()
    media_list = inst.media_list_new([])
    list_player.set_media_list(media_list)
    player = list_player.get_media_player()
    if PLATFORM.startswith('linux'):
        player.set_xwindow(window['-VID_OUT-'].Widget.winfo_id())
    else:
        player.set_hwnd(window['-VID_OUT-'].Widget.winfo_id())
    
    while True:
        event, values = window.read(timeout=1000)       
        if event == sg.WIN_CLOSED:
            break
    
        if event == 'Play':
            list_player.play()
        if event == 'Pause':
            list_player.pause()
        if event == 'Stop':
            list_player.stop()
        if event == 'Cargar':
    
            media_list.add_media('Resultado/resultado.mp4')
            list_player.set_media_list(media_list)
    
        if player.is_playing():
            window['-MESSAGE_AREA-'].update("{:02d}:{:02d} / {:02d}:{:02d}".format(*divmod(player.get_time()//1000, 60),
                                                                         *divmod(player.get_length()//1000, 60)))
        else:
            window['-MESSAGE_AREA-'].update('Carga el vídeo para empezar' if media_list.count() == 0 else 'Listo para reproducir' )
    
    window.close()            
        
home()     