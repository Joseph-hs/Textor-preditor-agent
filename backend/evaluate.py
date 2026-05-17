from models.predictor import TextPredictor
from utils.corpus import load_corpus
from utils.tokenizer import SpanishTokenizer


def iter_examples(sentences, tokenizer):
    for sentence in sentences:
        tokens = tokenizer.tokenize(sentence)
        for index in range(1, len(tokens)):
            context = tokenizer.detokenize(tokens[:index]) + " "
            expected = tokens[index]
            yield context, expected


def evaluate():
    tokenizer = SpanishTokenizer()
    corpus = load_corpus()
    split_index = max(1, int(len(corpus) * 0.8))
    train_sentences = corpus[:split_index]
    test_sentences = corpus[split_index:]

    predictor = TextPredictor(train_sentences)

    total = 0
    top1 = 0
    top3 = 0
    top5 = 0
    reciprocal_rank = 0.0

    for context, expected in iter_examples(test_sentences, tokenizer):
        predictions = predictor.predict(context, max_suggestions=5)
        predicted_tokens = []

        for prediction in predictions:
            tokens = tokenizer.tokenize(prediction["word"])
            if tokens:
                predicted_tokens.append(tokens[0])

        if not predicted_tokens:
            continue

        total += 1

        if expected == predicted_tokens[0]:
            top1 += 1

        if expected in predicted_tokens[:3]:
            top3 += 1

        if expected in predicted_tokens[:5]:
            top5 += 1
            reciprocal_rank += 1 / (predicted_tokens.index(expected) + 1)

    if total == 0:
        print("No hay suficientes ejemplos para evaluar.")
        return

    print(f"Ejemplos evaluados: {total}")
    print(f"Top-1: {top1 / total:.3f}")
    print(f"Top-3: {top3 / total:.3f}")
    print(f"Top-5: {top5 / total:.3f}")
    print(f"MRR:   {reciprocal_rank / total:.3f}")


if __name__ == "__main__":
    evaluate()
