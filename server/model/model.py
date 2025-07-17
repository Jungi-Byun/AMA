import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from kobert_tokenizer import KoBERTTokenizer
from transformers import AutoModelForSequenceClassification

_llm_model = None
_llm_tokenizer = None
_device = None
_classifier_model = None
_classifier_tokenizer = None

def get_llm_model():
    fn = 'get_llm_model'
    global _llm_model, _llm_tokenizer, _device
   
    if _llm_model is None:
        model_name = "LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct"
        _llm_model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            trust_remote_code=True
        )
        _llm_tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        _llm_model.to(_device)
        print(f"[{fn}] create new instance")
    else :
        print(f"[{fn}] exist instance")
    return _llm_model, _llm_tokenizer, _device

def get_classifier_model():
    fn = 'get_classifier_model'
    global _classifier_model, _classifier_tokenizer

    if _classifier_model is None:
        checkpoint_path = "./kobert_saved_model"
        _classifier_model = AutoModelForSequenceClassification.from_pretrained(checkpoint_path)
        _classifier_tokenizer = KoBERTTokenizer.from_pretrained(checkpoint_path)
        print(f"[{fn}] create new instance")
    else:
        print(f"[{fn}] exist instance")
    
    return _classifier_model, _classifier_tokenizer