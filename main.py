import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from mosec import Server, Worker


class Preprocess(Worker):
    def __init__(self):
        self.processor = WhisperProcessor.from_pretrained("openai/whisper-base")

    def forward(self, data):
        res = self.processor(data['array'], sampling_rate=data['sampling_rate'], return_tensors="pt")
        return res.input_features


class Inference(Worker):
    def __init__(self):
        self.model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-base")
        self.model.config.forced_decoder_ids = None
        self.device = torch.cuda.current_device() if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

    def forward(self, data):
        ids = self.model.generate(torch.cat(data).to(self.device))
        return ids.cpu().tolist()


class Postprocess(Worker):
    def __init__(self):
        self.processor = WhisperProcessor.from_pretrained("openai/whisper-base")

    def forward(self, data):
        res = self.processor.batch_decode(data, skip_special_tokens=True)
        return [{"text": msg} for msg in res]


if __name__ == "__main__":
    server = Server()
    server.append_worker(Preprocess, num=2)
    server.append_worker(Inference, max_batch_size=16, max_wait_time=10)
    server.append_worker(Postprocess, num=2, max_batch_size=8, max_wait_time=5)
    server.run()