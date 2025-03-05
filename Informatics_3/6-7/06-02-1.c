#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int a = 0;

void *mythread1(void *dummy)
{

   pthread_t mythid;
   
   mythid = pthread_self();

   printf("Hello, Ruslan Sultanovich!\n");

   a = a-10;


   printf("Thread 1: %lu, Calculation result = %d\n", mythid, a);

   return NULL;
}

void *mythread2(void *dummy)
{

   pthread_t mythid;
   
   mythid = pthread_self();

   printf("Hello, Vladislav!\n");

   a = a+3;

   printf("Thread 2: %lu, Calculation result = %d\n", mythid, a);


   return NULL;
}

int main()
{
   pthread_t thid1, thid2, mythid; 
   int result;
    
   result = pthread_create( &thid1, (pthread_attr_t *)NULL, mythread1, NULL);

   if(result != 0){
      printf ("Error on thread1 create, return value = %d\n", result);
      exit(-1);
   }   
   
   result = pthread_create( &thid2, (pthread_attr_t *)NULL, mythread2, NULL);

   if(result != 0){
      printf ("Error on thread2 create, return value = %d\n", result);
      exit(-1);
   }  

   printf("Threads created, thid1 = %lu, thid2 = %lu\n", thid1, thid2);

   mythid = pthread_self();
   
   printf("Hello world!\n");

   a = a+20;
   
   printf("Main thread: %lu, Calculation result = %d\n", mythid, a);

   pthread_join(thid1, (void **)NULL);
   pthread_join(thid2, (void **)NULL);

   return 0;
}