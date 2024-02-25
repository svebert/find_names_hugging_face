from transformers import pipeline

class NameCleaner:
    POSITIVE_LIST = ['Ich', 'Du', 'Er', 'Sie', 'Wir', 'Ihr']

    def __init__(self) -> None:      
        self.classifier = pipeline("ner")
        self.positive_list = [elem.lower() for elem in NameCleaner.POSITIVE_LIST]

    def _replace_names__with_placeholders(self, text: str, result_names: dict) -> str:
        text_out=""
        end_idx = 0
        for idx, element_names in enumerate(result_names):
            text_out += text[end_idx: element_names['start']]
            text_out += f"<Name{idx}>"
            end_idx = element_names['end']
        text_out += text[end_idx:]           

        return text_out
    
    def _apply_positive_list(self, result_names: dict) -> dict:
        out_names = [] 
        for elem in result_names:
            if elem['word'].lower() not in self.positive_list:
                out_names.append(elem)
        return out_names
    
    def _join_word_fragments(self, result_names: dict) -> dict:
        current_elem = None
        out_names = []
        for elem in result_names:
            if len(elem['word']) == 1 or elem['word'].startswith("##"):
                if current_elem == None:
                    current_elem = elem
                    cnt = 1
                elif current_elem is not None and current_elem['end'] == elem['start']:
                    current_elem['end'] = elem['end']
                    current_elem['word'] += elem['word']
                    current_elem['score'] = max(elem['score'],  current_elem['score'])
                    cnt += 1
                else:
                    out_names.append(current_elem)
                    current_elem = None
            else:
                if current_elem is not None:
                    out_names.append(current_elem)
                    current_elem = None
                out_names.append(elem)

        return out_names

    def clean(self, text: str) -> str:
        result = self.classifier(text)
        result_names = [elem for elem in result if elem['entity'] == 'I-PER']
        result_names = self._join_word_fragments(result_names)
        result_names = self._apply_positive_list(result_names)
        return self._replace_names__with_placeholders(text, result_names)



if __name__ == "__main__":

    text1 = "Du Jürgen, ich bin der Herbert und ihr habt alle eure Namen und könnt sie behalten"          
    target = text1.replace("Jürgen", "<Name0>").replace("Herbert", "<Name1>")
    nc = NameCleaner()
    cleaned_text = nc.clean(text=text1)
    assert cleaned_text == target