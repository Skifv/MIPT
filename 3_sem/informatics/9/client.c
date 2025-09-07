#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/msg.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>

#if 0
#define prn fprintf(stderr, "%d: %s\n", __LINE__, __func__);
#else
#define prn
#endif

#define SERVER 1
#define N 100

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

int main(void)
{ 
    int msqid;
    char pathname[]="server.c";
    key_t  key;
    int i,len;
    int client_id = getpid(); 

    /* Create or attach message queue  */
    
    key = ftok(pathname, 0);
    
    if ((msqid = msgget(key, 0666 | IPC_CREAT)) < 0){
       printf("Can\'t get msqid\n");
       exit(-1);
    }
     
    struct client client_msg;

    client_msg.mtype = SERVER;
    client_msg.message.id = client_id;

    struct server server_msg;

    // отправляемое сообщение
    
    strcpy(client_msg.message.request, "Hello, server!");

    if(msgsnd(msqid, (struct msgbuf *) &client_msg, sizeof(client_msg.message), 0) < 0){
       perror("msgsend");
       exit(-1);
    }

    if ((len = msgrcv(msqid, (struct msgbuf *) &server_msg, sizeof(server_msg.message), client_id, 0)) < 0){
       perror("msgrcv");
       exit(-1);
    }

    printf("Server response: <%s>\n", server_msg.message.response);

    return 0;    
}

