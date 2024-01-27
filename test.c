#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

/* define a struct called test_struct that contains three integers and a string pointer */

struct test_struct {
    int a;
    int b;
    int c;
    char *d;
};

/* main */

int main(int argc, char *argv[]) {
    /* declare a pointer to a struct called test_struct_ptr */
    struct test_struct *test_struct_ptr;

    /* allocate memory for the struct */
    test_struct_ptr = malloc(sizeof(struct test_struct));

    /* assign values to the struct's members */
    test_struct_ptr->a = 1;
    test_struct_ptr->b = 2;
    test_struct_ptr->c = 3;
    test_struct_ptr->d = "test";

    /* print the values of the struct's members */
    printf("a: %d\n", test_struct_ptr->a);
    printf("b: %d\n", test_struct_ptr->b);
    printf("c: %d\n", test_struct_ptr->c);
    printf("d: %s\n", test_struct_ptr->d);

    /* make an array of test_struct */
    struct test_struct test_struct_array[10];
    test_struct_array[0].a = 1;
    test_struct_array[0].b = 2;
    test_struct_array[0].c = 3;
    test_struct_array[0].d = "testweirdthing";

    test_struct_array[1].a = 4;
    test_struct_array[1].b = 5;
    test_struct_array[1].c = 6;
    test_struct_array[1].d = "test2";

    /* print the values of the struct's members */
    printf("a: %d\n", 0[test_struct_array].a);
    printf("b: %d\n", 0[test_struct_array].b);
    printf("c: %d\n", 0[test_struct_array].c);
    printf("d: %s\n", 0[test_struct_array].d);


    /* free the memory allocated for the struct */
    free(test_struct_ptr);

    return 0;
}
