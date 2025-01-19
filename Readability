#include <cs50.h>
#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

int count_letters(string input);
int count_words(string input);
int count_sentences(string input);

int main(void)
{
    float L, S;
    int letters, words, sentences, index;
    string input = get_string("Text: ");
    letters = count_letters(input);
    words = count_words(input);
    sentences = count_sentences(input);
    L = (letters / (float) words) * 100;
    S = (sentences / (float) words) * 100;
    index = round(0.0588 * L - 0.296 * S - 15.8);
    if (index > 16)
    {
        printf("Grade 16+\n");
    }
    else if (index < 1)
    {
        printf("Before Grade 1\n");
    }
    else
    {
        printf("Grade %i\n", index);
    }
}

int count_letters(string input)
{
    int length = strlen(input), sum = 0;
    for (int i = 0; i < length; i++)
    {
        if (isalpha(input[i]))
        {
            sum++;
        }
    }
    return sum;
}

int count_words(string input)
{
    int length = strlen(input), sum = 0;
    for (int i = 0; i < length; i++)
    {
        if (input[i] == ' ')
        {
            sum++;
        }
    }
    return sum + 1;
}

int count_sentences(string input)
{
    int length = strlen(input), sum = 0;
    for (int i = 0; i < length; i++)
    {
        if (input[i] == '!' || input[i] == '?' || input[i] == '.')
        {
            sum++;
        }
    }
    return sum;
}
