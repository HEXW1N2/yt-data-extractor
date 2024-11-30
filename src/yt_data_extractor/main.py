import PySimpleGUI as sg
import os
import sys
from pathlib import Path
from youtube_extractor import YouTubeExtractor
import logging

class YouTubeToolGUI:
    def __init__(self):
        sg.theme('DarkBlue3')
        
        # Get the installation directory
        self.base_dir = self._get_installation_dir()
        self.default_output = os.path.join(self.base_dir, 'data') if self.base_dir else None

        self.layout = [
            [sg.Text('YouTube Metadata Extractor', font=('Helvetica', 16), justification='center')],
            
            # URL Input Section
            [sg.Frame('Input', [
                [sg.Text('Single URL:')],
                [sg.Input(key='-URL-', size=(60, 1))],
                [sg.Text('OR')],
                [sg.Text('Batch File:')],
                [sg.Input(key='-BATCH-', size=(52, 1)), sg.FileBrowse(file_types=(("Text Files", "*.txt"),))]
            ])],
            
            # Output Directory Section
            [sg.Frame('Output', [
                [sg.Text('Select output directory:')],
                [sg.Input(default_text=self.default_output, key='-OUTPUT-', size=(52, 1)), 
                 sg.FolderBrowse(initial_folder=self.default_output)],
                [sg.Checkbox('Create timestamp subfolder', key='-TIMESTAMP-', default=True)]
            ])],
            
            # Progress Section
            [sg.Frame('Progress', [
                [sg.Multiline(size=(70, 10), key='-PROGRESS-', autoscroll=True, reroute_stdout=True)],
                [sg.ProgressBar(100, orientation='h', size=(50, 20), key='-PBAR-')]
            ])],
            
            # Control Buttons
            [sg.Button('Process Single URL', size=(15, 1)),
             sg.Button('Process Batch', size=(15, 1)),
             sg.Button('Clear', size=(15, 1)),
             sg.Button('Exit', size=(15, 1))]
        ]
        
        self.window = sg.Window('YouTube Metadata Extractor', self.layout, finalize=True)

    def _get_installation_dir(self):
        """Find the installation directory by looking for the 'data' folder"""
        try:
            # First check if we're in the installation directory
            if os.path.exists('data'):
                return os.getcwd()
            
            # Check parent directory
            parent = os.path.dirname(os.getcwd())
            if os.path.exists(os.path.join(parent, 'data')):
                return parent
            
            # If not found, use current directory
            return os.getcwd()
        except Exception as e:
            logging.error(f"Error finding installation directory: {e}")
            return os.getcwd()

    def update_progress(self, message):
        self.window['-PROGRESS-'].print(message)
        
    def process_url(self, url, extractor):
        self.update_progress(f"\nProcessing URL: {url}")
        success = extractor.extract_metadata(url, self.update_progress)
        if success:
            self.update_progress(f"Successfully processed: {url}")
        else:
            self.update_progress(f"Failed to process: {url}")
        return success
            
    def run(self):
        while True:
            event, values = self.window.read()
            
            if event in (sg.WIN_CLOSED, 'Exit'):
                break
                
            if event == 'Clear':
                self.window['-URL-'].update('')
                self.window['-BATCH-'].update('')
                self.window['-PROGRESS-'].update('')
                continue
                
            # Get output directory
            output_dir = values['-OUTPUT-']
            if not output_dir:
                output_dir = self.default_output
                self.window['-OUTPUT-'].update(output_dir)
            
            # Create output directory if it doesn't exist
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                sg.popup_error(f'Error creating output directory: {str(e)}')
                continue
                
            # Create timestamp subfolder if requested
            if values['-TIMESTAMP-']:
                from datetime import datetime
                output_dir = os.path.join(output_dir, datetime.now().strftime('%Y%m%d_%H%M%S'))
                os.makedirs(output_dir, exist_ok=True)
                
            extractor = YouTubeExtractor(output_dir)
            
            if event == 'Process Single URL':
                url = values['-URL-'].strip()
                if not url:
                    sg.popup_error('Please enter a URL')
                    continue
                    
                self.process_url(url, extractor)
                
            elif event == 'Process Batch':
                batch_file = values['-BATCH-']
                if not batch_file or not os.path.exists(batch_file):
                    sg.popup_error('Please select a valid batch file')
                    continue
                    
                try:
                    with open(batch_file, 'r') as f:
                        urls = [line.strip() for line in f if line.strip()]
                        
                    total_urls = len(urls)
                    for i, url in enumerate(urls, 1):
                        self.update_progress(f"\nProcessing URL {i}/{total_urls}")
                        self.window['-PBAR-'].update(current_count=(i * 100) // total_urls)
                        self.process_url(url, extractor)
                        
                except Exception as e:
                    self.update_progress(f"Error processing batch file: {str(e)}")
                    logging.exception("Error processing batch file")
                    
        self.window.close()

if __name__ == "__main__":
    try:
        gui = YouTubeToolGUI()
        gui.run()
    except Exception as e:
        logging.exception("Unexpected error in main")
        sg.popup_error(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)
