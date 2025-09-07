#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/msg.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

#if 0
#define prn fprintf(stderr, "%d: %s\n", __LINE__, __func__);
#else
#define prn
#endif

#define SERVER 1
#define N 100

int msqid;

/* Схема клиент-сервер */

   struct client {
      long mtype;
      struct {
         long id;
         char request[N]; // отправляемое сообщение, можно расширить
      } message;
   };

   struct server {
      long mtype;
      struct {
         char response[N]; // ответ от сервера, можно расширить
      } message;
   };


void * response(void * arg)
{
   struct client client_msg = *(struct client *) arg;
   struct server server_msg;
   
   server_msg.mtype = client_msg.message.id;

   snprintf(server_msg.message.response, 2*N, "Hello, client %ld!", client_msg.message.id);
   
   if ((msgsnd(msqid, (struct msgbuf *) &server_msg, sizeof(server_msg.message), 0)) < 0){
      perror("msgsnd");
      exit(-1);
   }  

   printf("Request from client %ld processed. \n", client_msg.message.id);

   return NULL;   
}


int main(void)
{
   char pathname[]="server.c";
   key_t  key;
   int i,len;

   /* Create or attach message queue  */
   
   key = ftok(pathname, 0);
   
   if ((msqid = msgget(key, 0666 | IPC_CREAT)) < 0){
      printf("Can\'t get msqid\n");
      exit(-1);
   }

   struct client client_msg;

   printf("Server is on, waiting messages.\n");

   while(1)
   {

      if ((len = msgrcv(msqid, (struct msgbuf *) &client_msg, sizeof(client_msg.message), SERVER, 0)) < 0){
         perror("msgrcv");
         exit(-1);
      }  

      printf("Got message from client %ld: <%s>\n", client_msg.message.id, client_msg.message.request);

      struct client client_msg_copy;

      // копируем сообщение клиента, чтобы передать в нить исполнения
      client_msg_copy.mtype = client_msg.message.id;
      client_msg_copy.message.id = client_msg.message.id;
      strncpy(client_msg_copy.message.request, client_msg.message.request, strlen(client_msg.message.request) + 1);
      
      pthread_t thread;
      pthread_create(&thread, NULL, response, &client_msg_copy);
   }

   return 0;    
}


