import os


def read_files(file_paths):
  text = ""
  for file_path in file_paths:
    with open(file_path, "r", encoding="KOI8-R") as file:
      text += file.read()
  return text

  
def load_questions(path_to_questions_folder):

  file_paths = [
        os.path.join(path_to_questions_folder, file_name)
        for file_name in os.listdir(path_to_questions_folder)
    ]
  
  files_content = read_files(file_paths)
  
  text_lines = files_content.split('\n\n')
  questions = {}
  
  for index, value in enumerate(text_lines):
    if 'Вопрос' in value:
      question = value.split(':')[1].replace('\n', ' ')
      answer = text_lines[index+1].split(':')[1].replace('\n', '')
      questions[question] = answer
  return questions
