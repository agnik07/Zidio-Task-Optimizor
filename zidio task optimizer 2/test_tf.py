import tensorflow as tf

# Check if TensorFlow is working
print("TensorFlow version:", tf.__version__)

# Create a small tensor and print it
tensor = tf.constant([[1, 2], [3, 4]])
print("Tensor:", tensor)