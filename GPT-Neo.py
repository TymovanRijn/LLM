from transformers import pipeline
import time
start_time = time.time()
generator = pipeline('text-generation', model='EleutherAI/gpt-neo-1.3B')
text = generator("Why are banana's not straight?", do_sample=True, min_length=100)


print(text[0]['generated_text'])
elapsed_time = time.time() - start_time
print("Totale uitvoertijd: ", elapsed_time, " seconden.")