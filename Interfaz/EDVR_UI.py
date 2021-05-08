import PySimpleGUI as sg
import ffmpeg
import os
import cv2
import shutil
import vlc
from sys import platform as PLATFORM    
    
    
def home():
    sg.theme('Black')
    layout = [ [sg.Text('Recuerda que solo puede procesar videos 720x1280 o viceversa')],
          [sg.Text('Elige un .mp4 para porcesar')],
          [sg.Input(size=(50,1), key='-OUT-')],
          [sg.Button('Buscar')],
          [sg.Checkbox('Quieres usar Predeblur?', key='-IN-')],
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
            path_v = values['-OUT-']
            ejecucion(path_v,predb)
    window.close()


def ejecucion(path_v,predb):
    layout = [[sg.Text('Cuando estes listo presiona Generar',size=(55, 1),key='-TEXT-')],
         [sg.Image(None,key='-IMAGE-')],
         [sg.Button("Generar"), sg.Button('Exit')]]
    window = sg.Window('EDVR UI', layout)
    while True: # Event Loop
        event, values = window.read()
        print(event, values)
        if event in (None, 'Exit'):
            break
        if event == 'Generar':
            window['-TEXT-'].update('Generando los frames, puede tardar un poco.')
            window['-IMAGE-'].update('Interfaz/frames.PNG')
            window.Refresh()
            vid=cv2.VideoCapture(path_v)
            altura=int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
            ancho=int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
            hacer_frames(path_v, altura, ancho)
            number_frames = len(os.listdir('./miVideo/data/000'))
            window['-TEXT-'].update('Generando los frames LQ, puede tardar un poco.')
            window['-IMAGE-'].update('Interfaz/LQ.PNG')
            window.Refresh()
            hacer_LR3()
            window['-TEXT-'].update('EDVR esta procesando las imágenes.')
            window['-IMAGE-'].update('Interfaz/EDVR.PNG')
            window.Refresh()
            #Progressbar 
            ejecutar_EDVR(number_frames, predb, altura, ancho)
            window['-TEXT-'].update('Generando el vídeo a partir de las imágenes.')
            window['-IMAGE-'].update('Interfaz/video.PNG')
            window.Refresh()
            hacer_video()
            window.extend_layout(window, [[sg.B('Sí')]])
            window['-TEXT-'].update('El proceso ya acabado, ¿Quieres visualizar el vídeo?')
            window['-IMAGE-'].update('Interfaz/video.PNG')
            window.Refresh()
        if event == 'Sí':
            print("Ver Video")
            reproducir_video()
            
    window.close()


#Adaptacion https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Media_Player_VLC_Based.py 
def btn(name):  # a PySimpleGUI "User Defined Element" (see docs)
    return sg.Button(name, size=(6, 1), pad=(1, 1))
    
def reproducir_video():
    layout = [[sg.Button('load')],
              [sg.Image('', size=(300, 170), key='-VID_OUT-')],
              [btn('previous'), btn('play'), btn('next'), btn('pause'), btn('stop')],
              [sg.Text('Load media to start', key='-MESSAGE_AREA-')]]
    
    window = sg.Window('Mini Player', layout, element_justification='center', finalize=True, resizable=True)
    
    window['-VID_OUT-'].expand(True, True)                # type: sg.Element
    #------------ Media Player Setup ---------#
    
    inst = vlc.Instance()
    list_player = inst.media_list_player_new()
    media_list = inst.media_list_new([])
    list_player.set_media_list(media_list)
    player = list_player.get_media_player()
    if PLATFORM.startswith('linux'):
        player.set_xwindow(window['-VID_OUT-'].Widget.winfo_id())
    else:
        player.set_hwnd(window['-VID_OUT-'].Widget.winfo_id())
    
    #------------ The Event Loop ------------#
    while True:
        event, values = window.read(timeout=1000)       # run with a timeout so that current location can be updated
        if event == sg.WIN_CLOSED:
            break
    
        if event == 'play':
            list_player.play()
        if event == 'pause':
            list_player.pause()
        if event == 'stop':
            list_player.stop()
        if event == 'next':
            list_player.next()
            list_player.play()
        if event == 'previous':
            list_player.previous()      # first call causes current video to start over
            list_player.previous()      # second call moves back 1 video from current
            list_player.play()
        if event == 'load':
    
            media_list.add_media('miVideo/movie.mp4')
            list_player.set_media_list(media_list)
    
        # update elapsed time if there is a video loaded and the player is playing
        if player.is_playing():
            window['-MESSAGE_AREA-'].update("{:02d}:{:02d} / {:02d}:{:02d}".format(*divmod(player.get_time()//1000, 60),
                                                                         *divmod(player.get_length()//1000, 60)))
        else:
            window['-MESSAGE_AREA-'].update('Load media to start' if media_list.count() == 0 else 'Ready to play media' )
    
    window.close()    
    
def hacer_frames(path_v, altura, ancho): 
    # Ojo las dimensiones del video hay que cambairlas, o pasarlas por argumento 
    resolucion=str(altura) + 'x' + str(ancho)
    
    if os.path.exists('./miVideo/data/000'):
        shutil.rmtree("./miVideo/data/000")
        
    os.mkdir("./miVideo/data/000")
    
    try:
        (ffmpeg.input(path_v)
              .filter('fps', fps=30)
              .output('./miVideo/data/000/%08d.png', 
                      video_bitrate='5000k',
                      s=resolucion,
                      sws_flags='bilinear',
                      start_number=0)
              .run(capture_stdout=True, capture_stderr=True))
    except ffmpeg.Error as e:
        print('stdout:', e.stdout.decode('utf8'))
        print('stderr:', e.stderr.decode('utf8'))    

        
def hacer_LR3():
    #Adaptacion de https://github.com/wqi/img-downsampler 
    if os.path.exists('./miVideo/data_LRx4/000'):
        shutil.rmtree("./miVideo/data_LRx4/000")
        
    os.mkdir("./miVideo/data_LRx4/000")
    
    hr_image_dir = 'miVideo/data/000'
    lr_image_dir = 'miVideo/data_LRx4/000'
    
    supported_img_formats = (".bmp", ".dib", ".jpeg", ".jpg", ".jpe", ".jp2",
                             ".png", ".pbm", ".pgm", ".ppm", ".sr", ".ras", ".tif",
                             ".tiff")
    
    # Downsample HR images
    for filename in os.listdir(hr_image_dir):
        if not filename.endswith(supported_img_formats):
            continue
    
        # Read HR image
        hr_img = cv2.imread(os.path.join(hr_image_dir, filename))
    
        # Blur with Gaussian kernel of width sigma=1
        hr_img = cv2.GaussianBlur(hr_img, (0, 0), 1, 1)
    
        # Downsample image 4x
        lr_img_4x = cv2.resize(hr_img, (0, 0), fx=0.25, fy=0.25,
                               interpolation=cv2.INTER_CUBIC)
    
        cv2.imwrite(os.path.join(lr_image_dir, filename), lr_img_4x)        
            

def ejecutar_EDVR(number_frames, predb, altura, ancho):
    if os.path.exists('basicsr/data/meta_info/meta_info_MIO_2.txt'):
         os.remove('basicsr/data/meta_info/meta_info_MIO_2.txt') 
    # igual con open lo crea.
    os.mknod('basicsr/data/meta_info/meta_info_MIO_2.txt') 
    
    meta_info=open('basicsr/data/meta_info/meta_info_MIO_2.txt','w')
    meta_info.write("000 " + str(number_frames) +" (" + str(ancho) + "," + str(altura) + ",3)\n")
    meta_info.close()
    
    test =open('options/test/EDVR/test_EDVR_L_x4_SR_Mio.yml', "r")
    list_of_lines = test.readlines()
    if predb ==True: 
        list_of_lines[32] = "  with_predeblur: true\n"
        list_of_lines[37] = "  pretrain_network_g: experiments/pretrained_models/EDVR/EDVR_L_x4_SRblur_REDS_official-983d7b8e.pth\n"
    elif predb ==False: 
         list_of_lines[32] = "  with_predeblur: false\n"
         list_of_lines[37] = "  pretrain_network_g: experiments/pretrained_models/EDVR/EDVR_L_x4_SR_REDS_official-9f5f5039.pth\n"

    test =open('options/test/EDVR/test_EDVR_L_x4_SR_Mio.yml', "w")
    test.writelines(list_of_lines)
    test.close()
    os.environ['MKL_THREADING_LAYER'] = 'GNU'
    print("antes")
    os.system('PYTHONPATH=”./:${PYTHONPATH}”')
    print("ptthonpath")
    os.system('CUDA_VISIBLE_DEVICES=0')
    print("cuda")
    os.system('python basicsr/test.py -opt options/test/EDVR/test_EDVR_L_x4_SR_Mio.yml') 
    print("edvr")

    
def hacer_video(): 
    if os.path.exists('miVideo/movie.mp4'):
        os.remove('miVideo/movie.mp4')
    
    try:
        (ffmpeg.input('results/EDVR_L_x4_Mio/visualization/REDS4/000/*.png', pattern_type='glob', framerate=30)
            .output('miVideo/movie.mp4', crf=20, preset='slower', movflags='faststart', pix_fmt='yuv420p')
            .run(capture_stdout=True, capture_stderr=True)
    )
    except ffmpeg.Error as e:
        print('stdout:', e.stdout.decode('utf8'))
        print('stderr:', e.stderr.decode('utf8'))    
        
home()     