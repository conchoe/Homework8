How far did the agent get? Did it fully implement your spec? What percentage of your acceptance criteria passed on the first try?

    The agent got really far with the spec. I spent most of the time on this assignment writing the spec so I think that it paid off. It passed 100% of my acceptance criteria on the first try and was 35/40 overall, with most of the WARN signs being for code quality/logic issues.

Where did you intervene? List each time you had to step in during Phase 2. Why was the intervention needed? Could a better spec have prevented it?

    I didn't intervene during the creation process. 

How useful was the AI review? Did it catch real bugs? Did it miss anything important? Did it flag things that weren't actually problems?

    The AI review was very helpful, it helped catch bugs that would've taken a long time to catch either by reading code or playing around with the quiz app for a long time. It caught that the difficulty distribution of questions for the Bronze rank was slightly off and it was an easy fix to change. There were no large bugs that caused the program to work in a way that violated the spec, but the review process did catch a lot of minor UX issues that might affect user experience. The review also did catch a lot of non-issues, giving a warning flag for problems that are handled by the program, for example, the potential division by 0 warning, which is guarded against by an if statement. 

Spec quality → output quality: In hindsight, what would you change about your spec to get a better result from the agent?

    I would be even more precise than I already was, giving specific numbers for the amount I want someone's ELO to increase by or decrease by or precisely how much I want the probabilty of a question to be picked to be increased or decreased if a question is liked or disliked. I also would put some stylistic specifications in so that it produces more readable code. 

When would you use this workflow? Based on this experience, when do you think plan-delegate-review is better than conversational back-and-forth? When is it worse?

    I think that this method is very useful when you have a concrete plan and idea on what your app to be like. Personally, I think that starting with a conversational back-and-forth to create the spec and exactly what you want in your app and then putting that spec to an agent would be the most optimal way to leverage AI. I also think that the test cases and having the agent review your program with those test cases is extremely helpful to counteract the biggest pitfall of AI generated code: safety. It is very difficult to reason about AI generated code and ensure that it does what you want, so having a separate agent go in and do that for you as well is a game changer. 
