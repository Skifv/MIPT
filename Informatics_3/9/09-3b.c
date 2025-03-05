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

    /* Получаем числа и увеличиваем их на 5 и 10 */

    for (i = 1; i <= 2; i++){
        mybuf.mtype = 1;

        if (( len = msgrcv(msqid, (struct msgbuf *) &mybuf, sizeof(mybuf.number), mybuf.mtype, 0)) < 0){
            printf("Can\'t receive message from queue\n");
            msgctl(msqid, IPC_RMID, (struct msqid_ds *) NULL);
            exit(-1);
        }

        mybuf.number += 5 * i;
        mybuf.mtype = 2;
        
        if(msgsnd(msqid, (struct msgbuf *) &mybuf, sizeof(mybuf.number), 0) < 0){
            printf("Can\'t send message to queue\n");   
            msgctl(msqid, IPC_RMID, (struct msqid_ds *) NULL);
            exit(-1);
        }
    }

    return 0;
}
