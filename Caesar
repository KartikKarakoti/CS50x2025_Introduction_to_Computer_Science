#include <cs50.h>
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, string argv[])
{
    if (argc != 2)
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }
    int length = strlen(argv[1]);
    for (int i = 0; i < length; i++)
    {
        if (!(isdigit(argv[1][i])))
        {
            printf("Usage: ./caesar key\n");
            return 1;
        }
    }
    int k = atoi(argv[1]);
    if (k == 0)
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }
    string plaintext = get_string("plaintext: ");
    length = strlen(plaintext);
    char ciphertext[length];
    char ci;
    int i = 0;
    for (; i < length; i++)
    {
        if (isupper(plaintext[i]))
            ciphertext[i] = ((plaintext[i] - 65) + k) % 26 + 65;
        else if (islower(plaintext[i]))
            ciphertext[i] = ((plaintext[i] - 97) + k) % 26 + 97;
        else
            ciphertext[i] = plaintext[i];
    }
    ciphertext[i] = '\0';
    printf("ciphertext: %s\n", ciphertext);
}
