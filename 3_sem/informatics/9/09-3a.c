#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/msg.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#define N 200

int main(void)
{
    
    int msqid;
    char pathname[]="09-3a.c";
    key_t  key;
    int i,len;

    struct mymsgbuf
    {
       long mtype;
       int number;
    } mybuf;



    /* Create or attach message queue  */
    
    key = ftok(pathname, 0);
    
    if ((msqid = msgget(key, 0666 | IPC_CREAT)) < 0){
       printf("Can\'t get msqid\n");
       exit(-1);
    }


    /* Send information */
    
    for (i = 1; i <= 2; i++){
        mybuf.mtype = 1;
        mybuf.number = 50 * i;
        if (( len = msgsnd(msqid, (struct msgbuf *) &mybuf, sizeof(mybuf.number), 0)) < 0){
           printf("Can\'t send message to queue\n");
           exit(-1);
        }
    }

    // ожидаем, что первое число будет увеличено на 5, второе на 10

    for (i = 1; i <= 2; i++){
        mybuf.mtype = 2;
        if (( len = msgrcv(msqid, (struct msgbuf *) &mybuf, sizeof(mybuf.number), mybuf.mtype, 0)) < 0){
           printf("Can\'t receive message from queue\n");
           exit(-1);
        }

        if (mybuf.number != 50 * i + 5 * i) {
           printf("Received number %d, expected %d\n", mybuf.number, 50 * i + 5);
           exit(-1);
        }
        else
        {
            printf("All OK, received number %d\n", mybuf.number);
        }
    }    

    return 0;    
}

