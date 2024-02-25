from transformers import pipeline
import re

class NameCleaner:
    POSITIVE_LIST = ['Ich', 'Du', 'Er', 'Sie', 'Wir', 'Ihr']
    PLACEHOLDER = "<Name>"

    def __init__(self) -> None:      
        self.classifier = pipeline("ner")
        self.positive_list = [elem.lower() for elem in NameCleaner.POSITIVE_LIST]
        self.regex = re.compile(r"(<Name[0-9]*>[^\s\.,\?\!]+)+", re.IGNORECASE)

    def _replace_names_with_placeholders(self, text: str, result_names: dict) -> str:
        text_out=""
        end_idx = 0
        for element_names in result_names:
            text_out += text[end_idx: element_names['start']]
            text_out += self.PLACEHOLDER
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
        for idx, elem in enumerate(result_names):
            if len(elem['word']) == 1 or \
                elem['word'].startswith("##") or \
                (idx+1 < len(result_names) and elem['end'] == result_names[idx+1]['start']):
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
        if current_elem is not None:
            out_names.append(current_elem)
            current_elem = None
        return out_names
    
    def _fix_placeholders(self, text: str) -> str:
        return self.regex.sub(self.PLACEHOLDER, text)

    def clean(self, text: str) -> str:
        result = self.classifier(text)
        result_names = [elem for elem in result if elem['entity'] == 'I-PER']
        result_names = self._join_word_fragments(result_names)
        result_names = self._apply_positive_list(result_names)
        txt_out = self._replace_names_with_placeholders(text, result_names)
        return self._fix_placeholders(txt_out)



if __name__ == "__main__":

    text1 = "Namen sind schwierig. Liebe Leute! Ich bin Frau Emilia Amelie Müller-Hagenbutte. Das geht so nicht.;Namen sind schwierig."
    target = text1.replace("Emilia", "<Name>").replace("Amelie", "<Name>").replace("Müller-Hagenbutte", "<Name>")
    nc = NameCleaner()
    cleaned_text = nc.clean(text=text1)
    assert cleaned_text == target