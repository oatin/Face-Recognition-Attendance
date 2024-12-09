from fastapi import FastAPI, BackgroundTasks
from keras.models import Model
from keras.applications import MobileNetV2
from keras.layers import Dense, GlobalAveragePooling2D
from keras.optimizers import Adam
import tensorflow as tf
import shutil
import os

app = FastAPI()

@app.post("/train/")
def train_model(course_id: str, user_ids: list, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_training, course_id, user_ids)
    return {"status": "Training initiated", "course_id": course_id}

def run_training(course_id, user_ids):
    dataset_dir = prepare_dataset(course_id, user_ids)
    
    model = create_model(num_classes=len(user_ids))
    
    train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
        rescale=1.0/255.0,
        validation_split=0.2
    )
    train_generator = train_datagen.flow_from_directory(
        dataset_dir,
        target_size=(160, 160),
        batch_size=32,
        class_mode='categorical',
        subset='training'
    )
    validation_generator = train_datagen.flow_from_directory(
        dataset_dir,
        target_size=(160, 160),
        batch_size=32,
        class_mode='categorical',
        subset='validation'
    )

    model.fit(
        train_generator,
        epochs=10,
        steps_per_epoch=len(train_generator),
        validation_data=validation_generator,
        validation_steps=len(validation_generator)
    )

    model.save(f"models/{course_id}.keras")
    print(f"Training completed for course {course_id}")

def prepare_dataset(course_id, user_ids):
    base_dir = "data" 
    temp_dir = f"temp/{course_id}"
    
    #remove temp 
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    
    os.makedirs(temp_dir, exist_ok=True)
    
    #copy data user in the course
    for user_id in user_ids:
        user_dir = os.path.join(base_dir, str(user_id))
        target_dir = os.path.join(temp_dir, str(user_id))
        if os.path.exists(user_dir):
            shutil.copytree(user_dir, target_dir)
    
    return temp_dir

def create_model(num_classes):
    base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(160, 160, 3))
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(512, activation='relu')(x)
    predictions = Dense(num_classes, activation='softmax')(x)
    model = Model(inputs=base_model.input, outputs=predictions)
    for layer in base_model.layers:
        layer.trainable = False
    model.compile(optimizer=Adam(), loss='categorical_crossentropy', metrics=['accuracy'])
    return model
