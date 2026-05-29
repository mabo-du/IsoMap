import os
import shutil
from optimum.onnxruntime import ORTModelForFeatureExtraction, ORTQuantizer
from optimum.onnxruntime.configuration import AutoQuantizationConfig
from transformers import AutoTokenizer

def main():
    model_id = "allenai/scibert_scivocab_uncased"
    temp_dir = "assets/models/scibert_onnx_temp"
    save_dir = "assets/models/scibert_onnx_quantized"

    print(f"Downloading and exporting {model_id} to ONNX...")
    # 1. Download tokenizer and export model to ONNX
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = ORTModelForFeatureExtraction.from_pretrained(model_id, export=True)
    
    # Save the base ONNX model temporarily
    model.save_pretrained(temp_dir)
    
    print("Quantising to INT8 (dynamic quantization for CPU)...")
    # 2. Dynamic quantisation for generic CPU architectures
    qconfig = AutoQuantizationConfig.avx2(is_static=False, per_channel=True)
    quantizer = ORTQuantizer.from_pretrained(model)
    quantizer.quantize(save_dir=save_dir, quantization_config=qconfig)
    
    # 3. Save tokenizer
    print("Saving tokenizer...")
    tokenizer.save_pretrained(save_dir)
    
    # Clean up temp
    print("Cleaning up temporary unquantised files...")
    shutil.rmtree(temp_dir)
    
    print(f"Done! Quantised ONNX model saved to {save_dir}")

if __name__ == "__main__":
    os.makedirs("assets/models", exist_ok=True)
    main()
