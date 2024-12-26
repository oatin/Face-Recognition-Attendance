import os
import shutil
import requests
import tensorflow as tf
from .exceptions import ModelLoadError
from .logger import Logger

class ModelManager:
    def __init__(self, config):
        self.config = config
        self.logger = Logger(config['logging']['app_log'], 'ModelManager')
        self.cache_dir = os.path.join('models', 'cache')
        self.current_dir = os.path.join('models', 'current')
        
        # Create directories if they don't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(self.current_dir, exist_ok=True)

    def download_model(self, model_url, version):
        """Download model from server"""
        try:
            cache_path = os.path.join(self.cache_dir, f"model_v{version}")
            
            # Download model file
            response = requests.get(model_url, stream=True)
            response.raise_for_status()
            
            # Save model file
            with open(f"{cache_path}.h5", 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.logger.info(f"Successfully downloaded model v{version}")
            return f"{cache_path}.h5"

        except Exception as e:
            raise ModelLoadError(f"Failed to download model: {str(e)}")

    def activate_model(self, model_path):
        """Move model to current directory and verify it"""
        try:
            # Copy model to current directory
            filename = os.path.basename(model_path)
            current_path = os.path.join(self.current_dir, filename)
            shutil.copy2(model_path, current_path)
            
            # Verify model can be loaded
            try:
                tf.keras.models.load_model(current_path)
                self.logger.info(f"Successfully activated model: {filename}")
                return current_path
            except Exception as e:
                # If model verification fails, delete copied file
                os.remove(current_path)
                raise ModelLoadError(f"Model verification failed: {str(e)}")

        except Exception as e:
            raise ModelLoadError(f"Failed to activate model: {str(e)}")

    def cleanup_old_models(self, keep_versions=3):
        """Clean up old model versions from cache"""
        try:
            models = [f for f in os.listdir(self.cache_dir) if f.endswith('.h5')]
            if len(models) > keep_versions:
                models.sort()  # Sort by version number
                for model in models[:-keep_versions]:
                    os.remove(os.path.join(self.cache_dir, model))
                    self.logger.info(f"Removed old model: {model}")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")