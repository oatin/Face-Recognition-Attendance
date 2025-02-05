from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split

class FaceRecognitionModel:
    def __init__(self, num_classes):
        self.num_classes = num_classes
        
    def build_model(self):
        base_model = MobileNetV2(
            weights='imagenet',
            include_top=False,
            input_shape=(224, 224, 3)
        )
        
        # Freeze early layers
        for layer in base_model.layers[:-20]:
            layer.trainable = False
        
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(512, activation='relu')(x)
        x = Dropout(0.5)(x)
        x = Dense(256, activation='relu')(x)
        x = Dropout(0.3)(x)
        predictions = Dense(self.num_classes, activation='softmax')(x)
        
        model = Model(inputs=base_model.input, outputs=predictions)
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def train(self, X, y, batch_size=32, epochs=10, model_path='best_face_model.keras'):
        model = self.build_model()

        if len(set(y)) > len(y) * 0.2:
            test_size = 0.2
        else:
            test_size = max(1, len(set(y))) / len(y)

        try:
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=test_size, stratify=y, random_state=42
            )
        except ValueError:
            X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=test_size, random_state=42)

        train_datagen = ImageDataGenerator(
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True
        )

        train_generator = train_datagen.flow(X_train, y_train, batch_size=batch_size)

        # Callbacks
        checkpoint = ModelCheckpoint(
            model_path,
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        )
        
        early_stopping = EarlyStopping(
            monitor='val_accuracy',
            patience=10,
            restore_best_weights=True
        )

        history = model.fit(
            train_generator,
            epochs=epochs,
            validation_data=(X_val, y_val),  
            callbacks=[checkpoint, early_stopping]
        )

        return model, history