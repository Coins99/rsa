#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <assert.h>
#include <time.h>


// uses:

// rsa_encrypt.exe encrypt <input_file> <output_file> <key_file>;
// rsa_encrypt.exe decrypt <input_file> <output_file> <key_file>;


// Commands:

// encrypt - Encrypt the input file and save keys
// decrypt - Decrypt the input file using saved keys


// Function declarations
int digits(int t);
int gcd(int a, int b);
char* string_of_int(int t);
int int_of_string(char* s);
bool isprime(int v);
long long make_prime(int n);
long long* public_key(long long p, long long q);
long long private_key(long long p, long long q, long long e, long long lambda);
long long mod_mult(long long a, long long b, long long mod);
long long mod_exp(long long base, long long expo, long long mod);
long long* encrypt_string(char* str, long long e, long long n, int* out_length);
char* decrypt_string(long long* encrypted, int length, long long d, long long n);
int encrypt_file(char* input_file, char* output_file, char* key_file);
int decrypt_file(char* input_file, char* output_file, char* key_file);

int digits(int t) {
    if (t == 0) return 1;
    int count = 0;
    if (t < 0) t = -t;
    while (t != 0) {
        count++;
        t = t / 10;
    }
    return count;
}

int gcd(int a, int b) {
    if (b == 0) {
        return a;
    }
    return gcd(b, a % b);
}

char* string_of_int(int t) {
    int length = digits(t);
    char* result = malloc(sizeof(char) * (length + 1));
    if (!result) return NULL;
    result[length] = '\0';
    
    if (t == 0) {
        result[0] = '0';
        return result;
    }
    
    bool negative = t < 0;
    if (negative) t = -t;
    
    for (int i = length - 1; i >= (negative ? 1 : 0); i--) {
        result[i] = (t % 10) + '0';
        t /= 10;
    }
    
    if (negative) result[0] = '-';
    return result;
}

int int_of_string(char* s) {
    int result = 0;
    int sign = 1;
    int i = 0;
    
    if (s[0] == '-') {
        sign = -1;
        i = 1;
    }
    
    for (; s[i] != '\0'; i++) {
        result = result * 10 + (s[i] - '0');
    }
    return result * sign;
}

bool isprime(int v) {
    int i;
    if (v < 0) v = -v;
    if (v < 2 || (v > 2 && v % 2 == 0))
        return false;
    if (v == 2) return true;
    for (i = 3; i <= (int)sqrt((double)v); i += 2)
        if (v % i == 0)
            return false;
    return true;
}

long long make_prime(int n) {
    n = abs(n % 10);
    if (n == 0) n = 3;
    long long num1 = (rand() % (n * 10)) + 1;
    long long num2 = 9 + rand() % (100 - 9);
    long long maybe = num1 * num2;
    
    while (maybe > 2 && !isprime((int)maybe)) {
        maybe--;
        if (maybe < 3) maybe = 3;
    }
    return maybe;
}

long long* public_key(long long p, long long q) {
    long long* pair = malloc(sizeof(long long) * 2);
    if (!pair) return NULL;
    
    pair[0] = p * q;
    long long lambda = (p - 1) * (q - 1);
    long long e = 2;
    
    while (e < lambda && (!isprime((int)e) || gcd((int)e, (int)lambda) != 1)) {
        e++;
    }
    pair[1] = e;
    return pair;
}

long long private_key(long long p, long long q, long long e, long long lambda) {
    long long d = 1;
    while ((d * e) % lambda != 1) {
        d++;
        if (d > lambda) return -1;
    }
    return d;
}

long long mod_mult(long long a, long long b, long long mod) {
    long long result = 0;
    a = a % mod;
    while (b > 0) {
        if (b % 2 == 1)
            result = (result + a) % mod;
        a = (2 * a) % mod;
        b /= 2;
    }
    return result;
}

long long mod_exp(long long base, long long expo, long long mod) {
    long long result = 1;
    base = base % mod;
    while (expo > 0) {
        if (expo % 2 == 1)
            result = (result * base) % mod;
        expo = expo / 2;
        base = (base * base) % mod;
    }
    return result;
}

long long* encrypt_string(char* str, long long e, long long n, int* out_length) {
    int len = (int)strlen(str);
    *out_length = len;
    long long* temp = malloc(sizeof(long long) * len);
    if (!temp) return NULL;
    
    for (int i = 0; i < len; i++) {
        temp[i] = mod_exp((long long)(unsigned char)str[i], e, n);
    }
    return temp;
}

char* decrypt_string(long long* encrypted, int length, long long d, long long n) {
    char* decrypted = malloc(sizeof(char) * (length + 1));
    if (!decrypted) return NULL;
    
    for (int i = 0; i < length; i++) {
        long long decrypted_val = mod_exp(encrypted[i], d, n);
        decrypted[i] = (char)decrypted_val;
    }
    decrypted[length] = '\0';
    return decrypted;
}



int encrypt_file(char* input_file, char* output_file, char* key_file) {
    FILE* infile = fopen(input_file, "rb");
    if (!infile) {
        printf("Error: Cannot open input file '%s'\n", input_file);
        return 1;
    }
    fseek(infile, 0, SEEK_END);
    long file_size = ftell(infile);
    fseek(infile, 0, SEEK_SET);
    if (file_size == 0) {
        printf("Error: Input file is empty\n");
        fclose(infile);
        return 1;
    }

    // Read 
    char* buffer = malloc(file_size + 1);
    if (!buffer) {
        printf("Error: Memory allocation failed\n");
        fclose(infile);
        return 1;
    }
    size_t bytes_read = fread(buffer, 1, file_size, infile);
    buffer[bytes_read] = '\0';
    fclose(infile);
    if (bytes_read < 2) {
        printf("Error: File must contain at least 2 characters\n");
        free(buffer);
        return 1;
    }
    srand((unsigned int)time(NULL));
    int num1 = (unsigned char)buffer[0] % 10;
    int num2 = (unsigned char)buffer[1] % 10;
    long long prime1 = make_prime(num1);
    long long prime2 = make_prime(num2);
    long long* keys = public_key(prime1, prime2);
    if (!keys) {
        printf("Error: Key generation failed\n");
        free(buffer);
        return 1;
    }
    long long n_value = keys[0];
    long long e_value = keys[1];
    long long lambda = (prime1 - 1) * (prime2 - 1);
    long long d_value = private_key(prime1, prime2, e_value, lambda);
    if (d_value == -1) {
        printf("Error: Private key generation failed\n");
        free(buffer);
        free(keys);
        return 1;
    }
    int encrypted_length;
    long long* encrypted = encrypt_string(buffer, e_value, n_value, &encrypted_length);
    if (!encrypted) {
        printf("Error: Encryption failed\n");
        free(buffer);
        free(keys);
        return 1;
    }
    
    // Save encrypted data
    FILE* outfile = fopen(output_file, "w");
    if (!outfile) {
        printf("Error: Cannot create output file '%s'\n", output_file);
        free(buffer);
        free(keys);
        free(encrypted);
        return 1;
    }
    for (int i = 0; i < encrypted_length; i++) {
        fprintf(outfile, "%lld", encrypted[i]);
        // if (i < encrypted_length - 1) fprintf(outfile, ",");
    }
    fclose(outfile);
    FILE* keyfile = fopen(key_file, "w");
    if (!keyfile) {
        printf("Error: Cannot create key file '%s'\n", key_file);
        free(buffer);
        free(keys);
        free(encrypted);
        return 1;
    }
    fprintf(keyfile, "p=%lld\n", prime1);
    fprintf(keyfile, "q=%lld\n", prime2);
    fprintf(keyfile, "n=%lld\n", n_value);
    fprintf(keyfile, "e=%lld\n", e_value);
    fprintf(keyfile, "d=%lld\n", d_value);
    fprintf(keyfile, "length=%d\n", encrypted_length);
    fclose(keyfile);
    printf("Encryption successful!\n");
    printf("Public Key (n, e): (%lld, %lld)\n", n_value, e_value);
    printf("Private Key (d): %lld\n", d_value);
    printf("Encrypted %d characters\n", encrypted_length);
    free(buffer);
    free(keys);
    free(encrypted);
    return 0;
}

int decrypt_file(char* input_file, char* output_file, char* key_file) {
    // Read keys
    FILE* keyfile = fopen(key_file, "r");
    if (!keyfile) {
        printf("Error: Cannot open key file '%s'\n", key_file);
        return 1;
    }
    long long p, q, n, e, d;
    int length;
    if (fscanf(keyfile, "p=%lld\nq=%lld\nn=%lld\ne=%lld\nd=%lld\nlength=%d\n", 
               &p, &q, &n, &e, &d, &length) != 6) {
        printf("Error: Invalid key file format\n");
        fclose(keyfile);
        return 1;
    }
    fclose(keyfile);
    // Read encrypted data
    FILE* infile = fopen(input_file, "r");
    if (!infile) {
        printf("Error: Cannot open input file '%s'\n", input_file);
        return 1;
    }
    long long* encrypted = malloc(sizeof(long long) * length);
    if (!encrypted) {
        printf("Error: Memory allocation failed\n");
        fclose(infile);
        return 1;
    }
    for (int i = 0; i < length; i++) {
        if (fscanf(infile, "%lld", &encrypted[i]) != 1) {
            printf("Error: Invalid encrypted file format\n");
            free(encrypted);
            fclose(infile);
            return 1;
        }
        if (i < length - 1) {
            char comma;
            fscanf(infile, "%c", &comma);
        }
    }
    fclose(infile);
    // Decrypt
    char* decrypted = decrypt_string(encrypted, length, d, n);
    if (!decrypted) {
        printf("Error: Decryption failed\n");
        free(encrypted);
        return 1;
    }
    // Save decrypted data
    FILE* outfile = fopen(output_file, "wb");
    if (!outfile) {
        printf("Error: Cannot create output file '%s'\n", output_file);
        free(encrypted);
        free(decrypted);
        return 1;
    }
    fwrite(decrypted, 1, length, outfile);
    fclose(outfile);
    printf("Decryption successful!\n");
    printf("Decrypted %d characters\n", length);
    free(encrypted);
    free(decrypted);
    return 0;
}

int main(int argc, char* argv[]) {
    // Ensure we flush output immediately
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
    if (argc != 5) {
        fflush(stdout);
        return 1;
    }
    char* command = argv[1];
    char* input_file = argv[2];
    char* output_file = argv[3];
    char* key_file = argv[4];
    if (strcmp(command, "encrypt") == 0) {
        return encrypt_file(input_file, output_file, key_file);
    }
    else if (strcmp(command, "decrypt") == 0) {
        return decrypt_file(input_file, output_file, key_file);
    }
    else {
        printf("Error: Unknown command '%s'\n", command);
        fflush(stdout);
        return 1;
    }
}