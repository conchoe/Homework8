Create a command line python quiz app with a local login. 

** File Structure **
app.py: main quiz logic
auth.py: user login logic 
data_manager.py: functions for reading and writing json files containing question banks and user information.
questions.json: The human-readable question bank that should be formatted like this :
{
  "questions": [
    {
      "question": "What keyword is used to define a function in Python?",
      "type": "multiple_choice",
      "options": ["func", "define", "def", "function"],
      "answer": "def",
      "category": "Python Basics",
      "difficulty": "Easy"
    },
    {
      "question": "A list in Python is immutable.",
      "type": "true_false",
      "answer": "false",
      "category": "Data Structures",
      "difficulty": "Easy"
    },
    {
      "question": "What built-in function returns the number of items in a list?",
      "type": "short_answer",
      "answer": "len",
      "category": "Python Basics",
      "difficulty": "Medium"
    }
    {
      "question": "what is the time complexity of binary search?",
      "type": "multiple_choice",
      "options":["O(N)", "O(N^2), "O(logN)", "O(NlogN)"],
      "answer": "O(logN)",
      "category": "Time Complexity",
      "difficulty": "Hard"
    }
    {
      "question": "The built-in search algorithm in Python is linear search",
      "type": "true_false",
      "answer": "true",
      "category": "Python Basics",
      "difficulty": "Medium"
    }
    
  ]
}
user_data.data: should be a non human readable file to store user information (username, password, statistics)
**** end file structure

1. On startup the app should greet the user and ask the user to log in with a username and password or sign up with a new username and password. These          usernames need to be unique and passwords should be required to have a reasonable level of complexity to them so that they aren't easily guessable. Use a simple hash function to hide the passwords. 
2. The app should then ask the user what level of proficiency they have in python if it is their first time on the app. This should then set a baseline difficulty for them as easy, medium, or hard.
3. Once the user has given their level of proficiency or if it is not their first time logging in they should then be taken to a main menu. This menu should include a Start Test option, a View Stats option and a Exit option.
When a user starts a test it should be 10 questions long and a mix of multiple choice, true or false, and short answer questions. For the short answer questions make them one or two words long, something like asking for a function name when given what it does. 
When a user views their stats they should see their level of proficiency. Use a video-game like ranking system with bronze being the lowest and diamond being the highest. ie. Bronze, Silver, Gold, Diamond. Have an elo system where a user gains elo if they get over 70% and lose elo if they get less than 70%. if they get right at 70% their elo should remain unchanged. These rankings should correspond with easy, medium and hard difficulties.
- bronze rank is baseline easy, silver is baseline medium, gold is baseline hard, and diamond is also baseline hard, with more hard questions that gold. 
They should also be able to see the number of quizzes they have taken and their overall correct answer rate and their rank. 
- ELO ranges BRONZE: 0 - 500
             SILVER: 501-1000
             GOLD: 1001-1500
             DIAMOND: 1501 + 

4. For a user who has a easy difficulty they should receive easy-medium difficulty questions.
    A user who has medium difficulty should receive easy-medium-hard difficulty questions.
    A user who has hard difficulty should receive mostly hard questions with some medium questions.
5. After every quiz ask the user was this test Easy, just right, or too hard? 
- if the user replies too easy, then the next test should contain more questions on the higher end of their difficulty spectrum.
- if the user replies just right, keep the distribution of difficulty of questions similar as the one previous.
- if the user replies too hard, then the next quiz should have more questions on the lower spectrum of their difficulty range.
- note these should take effect for the next quiz that they take. 
6. After each question the user should get an optional choice to say whether they dislike or like the question.
- if the user dislikes that question do not show that question anymore
- if a user likes a question show more questions of that difficulty level for the next quiz. 
7. When a user exits the app it should save their data. 

** ERROR HANDLING **
- If a user tries to create a username that already exists tell them that it is already taken and prompt them to enter a new one.
- For True/False or Multiple choice questions if a user inputs an invalid input ie. a number for an answer that is a word or a word for an answer that is a number or something that isnt true or false for a true or false question, the app should prompt the user to input an answer of the correct format, tell the user that their answer format was invalid.
- if questions.json is formatted incorrectly or is missing a question bank display incorrect formatting and/or missing question bank and terminate. 
- if a user inputs the wrong password more than 3 times then the program should shut down. 


** ACCEPTANCE CRITERIA ** 
- User can successfully create a username and password that persists after restarting the app
- if a user gets 100% on a quiz they gain elo, if they get a 90% they gain elo, but less than if they got a 100%
- if a user gets a 70% their elo should not change
- if a user gets below a 70% their elo should decrease
- if a user gets a 30% their elo should decrease more than if they got a 50%
- a user should be able to view their rank, how many tests they have taken, and their overall correctness rate. 
- a question marked as disliked should not appear for that user again
- a user who is bronze ranked should only receive easy - medium difficulty questions.
- a user who is silver ranked should only receive mostly medium questions with some easy and some hard questions difficulty questions.
- a user who is gold should receive mostly medium questions, and some hard questions.
- a user who is diamond should receive mostly hard questions. 








