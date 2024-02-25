from src.name_cleaner import NameCleaner
import csv
import warnings

class ExampleReader:

    def __init__(self, csv_filepath, text_column_name= 'text', target_column_name='target', delimieter=';') -> None:
        self.test_texts = []
        self.idx = -1
        with open(csv_filepath, "r", encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=delimieter)            
            for idx, row in enumerate(reader):
                print(row)
                if row[text_column_name] is not None and row[target_column_name] is not None:
                    self.test_texts.append({text_column_name: row[text_column_name],  target_column_name: row[target_column_name]})
                else:
                    warnings.WarningMessage(f"invalid data in {csv_filepath} in row {idx}")

    def __iter__(self) -> dict:
        return self

    def __next__(self):
        self.idx += 1
        if self.idx < len(self.test_texts):
            return self.test_texts[self.idx]
        raise StopIteration



def test_namecleaner_simple():
    text1 = "Hallo ich bin Hans Mustermann und will nicht, dass irgendwer meinen Namen liest. Es geht mir aber nur um den Namen, " \
            + "nicht um meine Adresse: Hamburg, Poppenbüttler Str. 57"
    target = text1.replace("Hans", "<Name0>").replace("Mustermann", "<Name1>")
    nc = NameCleaner()
    cleaned_text = nc.clean(text=text1)
    assert cleaned_text == target

def test_namecleaner_join_fragments():
    text1 = "Du Jürgen wo ist Heinz Herbert"           
    target = text1.replace("Jürgen", "<Name0>").replace("Heinz", "<Name1>").replace("Herbert", "<Name2>")
    nc = NameCleaner()
    cleaned_text = nc.clean(text=text1)
    assert cleaned_text == target

def test_namecleaner_positive_list():
    text1 = "Du Jürgen, ich bin der Herbert und ihr habt alle eure Namen und könnt sie behalten"          
    target = text1.replace("Jürgen", "<Name0>").replace("Herbert", "<Name1>")
    nc = NameCleaner()
    cleaned_text = nc.clean(text=text1)
    assert cleaned_text == target

def test_namecleaner_csv():
    text_column_name= 'text'
    target_column_name='target'
    er = ExampleReader('tests/test_data/texts.csv', text_column_name, target_column_name)

    nc = NameCleaner()

    for elem in er:
        text = elem[text_column_name]
        target = elem[target_column_name]
        cleaned_text = nc.clean(text=text)
        assert cleaned_text == target