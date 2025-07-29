import random
import pygame
import pygame_gui
from collections import deque

from pygame_gui.elements import UIButton, UIImage
import pygame_gui.elements.ui_2d_slider
from pygame_gui.windows import UIFileDialog
from pygame_gui.core.utility import create_resource_path

class Base:
    def __init__(self):
        pygame.init()

        window_size = (800, 600)
        pygame.display.set_caption('AR registration')
        self.window_surface = pygame.display.set_mode(window_size)
        self.ui_manager = pygame_gui.UIManager(window_size)


        self.background = pygame.Surface(window_size)
        self.background.fill(self.ui_manager.ui_theme.get_colour('dark_bg'))

        self.time_delta_stack = deque([])


        """ horizontal menu bar """
        menu_bar_height = 30
        self.menu_bar_rect = pygame.Rect(0, 0, window_size[0], menu_bar_height)
        self.menu_bar = pygame_gui.elements.UIPanel(
            relative_rect=self.menu_bar_rect,
            starting_height=1,
            manager=self.ui_manager,
            margins={'left': 0, 'right': 0, 'top': 0, 'bottom': 0},
            object_id='#menu_bar'
        )


        self.menu_button1 = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, 100, menu_bar_height),
            text='File',
            manager=self.ui_manager,
            container=self.menu_bar,
            object_id='#menu_button1'
        )

        self.file_dialog = None

        self.menu_button2 = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(100, 0, 100, menu_bar_height),
            text='Edit',
            manager=self.ui_manager,
            container=self.menu_bar,
            object_id='#menu_button2'
        )

        self.menu_button3 = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(200, 0, 100, menu_bar_height),
            text='View',
            manager=self.ui_manager,
            container=self.menu_bar,
            object_id='#menu_button3'
        )



        """ vertical panel """
        panel_width = 200
        self.panel_rect = pygame.Rect(window_size[0]-panel_width, menu_bar_height, panel_width, window_size[1]-menu_bar_height)
        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=self.panel_rect,
            starting_height=1,
            manager=self.ui_manager,
            margins={'left': 0, 'right': 0, 'top': 0, 'bottom': 0},
            object_id='#panel'
        )

        self.panel_button1 = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 10, 180, 30),
            text='Settings',
            manager=self.ui_manager,
            container=self.panel,
            object_id='#panel_button1'
        )

        self.panel_button2 = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 50, 180, 30),
            text='Help',
            manager=self.ui_manager,
            container=self.panel,
            object_id='#panel_button2'
        )

        self.panel_slider1 = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(10, 90, 180, 30),
            start_value=0.5,
            value_range=(0.0, 1.0),
            manager=self.ui_manager,
            container=self.panel,
            object_id='#panel_slider1'
        )

        self.panel_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=["select item", "item1", "item2", "item3"],
            starting_option='select item',
            relative_rect=pygame.Rect((10, 130), (180, 30)),
            manager=self.ui_manager,
            container=self.panel,
            object_id='#panel_dropdown1'
        )

        


        # clock for maintaining frame rate
        self.clock = pygame.time.Clock()
        self.is_running = True




    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            self.ui_manager.process_events(event)

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.menu_button1:
                    print('File menu pressed')
                    self.file_dialog = UIFileDialog(pygame.Rect(160, 50, 440, 500),
                                                    self.ui_manager,
                                                    window_title='Load Image...',
                                                    initial_file_path='data/images/',
                                                    allow_picking_directories=True,
                                                    allow_existing_files_only=True,
                                                    allowed_suffixes={""})
                    self.menu_button1.disable()

            if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
                # if self.display_loaded_image is not None:
                #     self.display_loaded_image.kill()
                try:
                    image_path = create_resource_path(event.text)
                    loaded_image = pygame.image.load(image_path).convert_alpha()
                    print('loaded image:', image_path)

                except pygame.error:
                    pass
                

 





    def run(self):
        while self.is_running:
            time_delta = self.clock.tick(60) / 1000.0
            self.time_delta_stack.append(time_delta)
            if len(self.time_delta_stack) > 2000:
                self.time_delta_stack.popleft()

            # check for input
            self.process_events()

            # respond to input
            self.ui_manager.update(time_delta)


            # render the screen
            self.window_surface.blit(self.background, (0, 0))
            self.ui_manager.draw_ui(self.window_surface)

            pygame.display.update()

        pygame.quit()

if __name__ == "__main__":
    app = Base()
    app.run()