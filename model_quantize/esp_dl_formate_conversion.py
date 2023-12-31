#import libraries 
from optimizer import *
from calibrator import *
from evaluator import *
import pickle
import numpy as np

#load ONNX model 
#name = "tf_model_final.onnx"
name = "algea_test.onnx"
print(name)
onnx_model = onnx.load(name)


#optimize ONNX model 
optimized_model_path = optimize_fp_model(name)


#load calibration dataset
X_cal_name = 'X_norm.pkl'
Y_cal_name = 'y_every.pkl'
with open(X_cal_name, 'rb') as f:
    (test_images) = pickle.load(f)
with open(Y_cal_name, 'rb') as f:
    (test_labels) = pickle.load(f)

calib_dataset = test_images[0:1800:20]
pickle_file_path = 'algea_calib.pickle'


#calibration 
model_proto = onnx.load(optimized_model_path)
print('Generating the quantization table:')
#calib = Calibrator('int16', 'per-tensor', 'minmax')


###for in8 conversion 
calib = Calibrator('int8', 'per-channel', 'minmax') 


calib.set_providers(['CPUExecutionProvider'])
# Obtain the quantization parameter
calib.generate_quantization_table(model_proto,calib_dataset, pickle_file_path)
# Generate the coefficient files for esp32s3
calib.export_coefficient_to_cpp(model_proto,  pickle_file_path, 'esp32s3', '.', 'algea_coefficientTRUE', True)

"""
#evaluation
print('Evaluating the performance on esp32s3:')
eva = Evaluator('int8', 'per-channel', 'esp32s3')
eva.set_providers(['CPUExecutionProvider'])
eva.generate_quantized_model(model_proto, pickle_file_path)

output_names = [n.name for n in model_proto.graph.output]
providers = ['CPUExecutionProvider']
m = rt.InferenceSession(optimized_model_path, providers=providers)
batch_size = 64
batch_num = int(len(test_images) / batch_size)
res = 0
fp_res = 0
input_name = m.get_inputs()[0].name
for i in range(batch_num):
    # int8_model
    [outputs, _] = eva.evaluate_quantized_model(test_images[i * batch_size:(i + 1) * batch_size], False)
    res = res + sum(np.argmax(outputs[0], axis=1) == test_labels[i * batch_size:(i + 1) * batch_size])

    # floating-point model
    fp_outputs = m.run(output_names, {input_name: test_images[i * batch_size:(i + 1) * batch_size].astype(np.float32)})
    fp_res = fp_res + sum(np.argmax(fp_outputs[0], axis=1) == test_labels[i * batch_size:(i + 1) * batch_size])
print('accuracy of int8 model is: %f' % (res / len(test_images)))
print('accuracy of fp32 model is: %f' % (fp_res / len(test_images)))
"""