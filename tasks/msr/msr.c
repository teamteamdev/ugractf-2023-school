// Console gui app with a menu, checking environment variables, command line arguments, and system information
// Target - linux x64, gcc
// Uses ncurses library, parses options with getopt_long

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <ncurses.h>
#include <time.h>
#include <getopt.h>
#include <signal.h>

#define MAX 100

#define DEBUG 0

char* SERVER_URL = "https://msr.s.2023.ugractf.ru/check"; // paste here

unsigned long long SECRET_NUMBER =  42;


char checksum[] = {/*CHECKSUM_PLACEHOLDER*/};
// char checksum[] = {233, 29, 216, 204, 222, 101, 72, 187, 193, 107, 222, 175, 227, 116, 71, 187, 123, 220, 192, 131, 109, 218, 232, 191, 205, 183, 114, 113, 104 };
int checksum_len = /*CHECKSUM_LEN_PLACEHOLDER*/0; // paste here

char *send_to_server = NULL;
int send_to_server_len = 0;

char HELP_TEXT[] = "This is help text, it is very long and it is very useful. If you don't read it, you will be punished.";
char CAT_ART_1[] = "           .'\\   /`.\n         .'.-.`-'.-.`.\n    ..._:   .-. .-.   :_...\n  .'    '-.(o ) (o ).-'    `.\n :  _    _ _`~(_)~`_ _    _  :\n:  /:   ' .-=_   _=-. `   ;\\  :\n:   :|-.._  '     `  _..-|:   :\n :   `:| |`:-:-.-:-:'| |:'   :\n  `.   `.| | | | | | |.'   .'\n    `.   `-:_| | |_:-'   .'\n      `-._   ````    _.-'\n          ``-------''\n";
char CAT_ART_2[] =  "  |\\---/|\n  | o_o |\n   \\_^_/\n";
char CAT_ART_3[] = "／l、\n（ﾟ､ ｡７\nl、ﾞ~ヽ\nじしf_, )ノ\n";
char CAT_ART_4[] = "ฅ^•ﻌ•^ฅ\n";


char* cat_arts[] = {CAT_ART_1, CAT_ART_2, CAT_ART_3, CAT_ART_4};

unsigned long long get_available_ram();
unsigned long long get_total_ram();
int get_cpu_count();
int get_current_day_name();
int get_current_day();

void print_message(char *msg);


unsigned char ror(unsigned char value, int count){
    const unsigned int mask = (8*sizeof(value) - 1);
    count &= mask;
    return (value >> count) | (value << ((-count) & mask));
}

unsigned char rol(unsigned char value, int count){
    const unsigned int mask = (8*sizeof(value) - 1);
    count &= mask;
    return (value << count) | (value >> ((-count) & mask));
}

char*  encrypt_1(char *str, int len, char *key, int key_len){
    char* dest = malloc(len);
    for (int i = 0; i < len; i++){
        dest[i] = str[i] ^ key[i % key_len];
        if (i % 2 == 0){
            dest[i] = ror(dest[i], 1);
        } else {
            dest[i] = rol(dest[i], 1);
        }
    }
    return dest;
}


char* encrypt_2(char *str, int len, char *key, int key_len){
    char* dest = malloc(len);
    for (int i = 0; i < len; i++){
        dest[i] = str[i] ^ key[i % key_len];
        if (i % 2 == 0){
            dest[i] = rol(dest[i], 3);
        } else {
            dest[i] = ror(dest[i], 2);
        }
    }
    return dest;
}


int check_system_requirements(){
    char *req_str = malloc(256);
    if (req_str == NULL){
        if (DEBUG){
            printf("Error allocating memory\n");
        }
        return 1;
    }
    int cpu_count = get_cpu_count();
    unsigned long long ram = get_available_ram();
    unsigned long long total_ram = get_total_ram();
    int day = get_current_day();
    int day_name = get_current_day_name();

    char *days[] = {"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"};

    char *current_day = days[day_name];

    sprintf(req_str, "%lld_%lld_%s_%d_%d_%lld", ram, total_ram, current_day, cpu_count, day, SECRET_NUMBER);
    // req_str = "3648_22289_Wednesday_33_94_42";

    int req_str_len = strlen(req_str);

    if (DEBUG){
        print_message(req_str);
    }
    char* enc1 = encrypt_1(req_str, req_str_len, CAT_ART_4, strlen(CAT_ART_4));
    
    if (DEBUG){
        //save to file
        FILE *f = fopen("req_str", "w");
        if (f == NULL){
            printf("Error opening file!\n");
            exit(1);
        }
        for (int i = 0; i < req_str_len; i++){
            fputc(enc1[i], f);
        }
        fclose(f);

    }

    for (int i = 0; i < req_str_len; i++){
        if (i >= checksum_len){
            if (DEBUG){
                print_message("System requirements not met1");
            }
                return 1;
        }
        if (enc1[i] != checksum[i]){
            if (DEBUG){
                print_message("System requirements not met2");
                printf("%d %d %d\n", i, enc1[i], checksum[i]);
            }
            return 1;
        }
    }
    if (DEBUG){
        print_message("System requirements met3");
    }
    send_to_server = encrypt_2(req_str, req_str_len, CAT_ART_3, strlen(CAT_ART_3));
    send_to_server_len = req_str_len;
    if (DEBUG){
        //save to file
        FILE *f = fopen("send_to_server", "w");
        if (f == NULL){
            printf("Error opening file!\n");
            exit(1);
        }
        for (int i = 0; i < req_str_len; i++){
            fputc(send_to_server[i], f);
        }
        fclose(f);

    }
    return 0;
}


void send_check_to_server(){
    // send check to server and get response
    // get flag parameter from response via curl and popen
    
    if (send_to_server == NULL){
        return;
    }
    char *cmd = malloc(256);
    if (cmd == NULL){
        if (DEBUG){
            printf("Error allocating memory\n");
        }
        return;
    }
    //urlencode send_to_server
    char *send_to_server_urlencoded = malloc(2*send_to_server_len+1);
    if (send_to_server_urlencoded == NULL){
        if (DEBUG){
            printf("Error allocating memory\n");
        }
        return;
    }
    int send_to_server_len = strlen(send_to_server);
    for (int i = 0; i < send_to_server_len; i++){
        sprintf(send_to_server_urlencoded + 2*i, "%02X", (unsigned char)send_to_server[i]);
    }
    if (DEBUG){
        print_message(send_to_server_urlencoded);
    }
    sprintf(cmd, "curl -s -X POST -d \"check=%s\" %s", send_to_server_urlencoded, SERVER_URL);
    if (DEBUG){
        print_message(cmd);
    }
    FILE *fp = popen(cmd, "r");
    if (fp == NULL){
        if (DEBUG){
            printf("Error opening pipe\n");
        }
        return;
    }
    char *response = malloc(256);
    if (response == NULL){
        if (DEBUG){
            printf("Error allocating memory\n");
        }
        return;
    }
    fgets(response, 256, fp);
    if (DEBUG){
        printf("Response: %s\n", response);
    }
    print_message(response);
    pclose(fp);
    free(cmd);
    free(response);
}
    

void print_cat(){
    // pick random cat ascii art
    srand(time(NULL));
    int cat = rand() % 4;
    printf("%s", cat_arts[cat]);
    exit(1);
}
            

int process_options(int argc, char *argv[], char *envp[]){

    /*
    Options list
    -h, --help        Display help
    --I_do_not_wanna_send_all_my_logs_to_fbi_but_I_agree_with_it_here_is_my_secret_code_for_this_operation <number>       Secret option
    -c --cat          Display cat ascii art

    */
    static struct option long_options[] = {
        {"help", no_argument, 0, 'h'},
        {"I_do_not_wanna_send_all_my_logs_to_fbi_but_I_agree_with_it_here_is_my_secret_code_for_this_operation", required_argument, 0, 0},
        {"cat", no_argument, 0, 'c'},
        {0, 0, 0, 0}
    };

    int option_index = 0;
    int c;

    while((c = getopt_long(argc, argv, "hd:c", long_options, &option_index)) != -1){
        switch(c){
            case 'h':
                puts(HELP_TEXT);
                exit(1);
                break;
            case 0:
                if (DEBUG){
                    printf("Dumret\n");
                }
                SECRET_NUMBER = atoll(optarg);
                printf("Secret number is %lld\n", SECRET_NUMBER);
                break;
            case 'c':
                if (DEBUG){
                    printf("Cat\n");
                }
                print_cat();
                break;
            case '?':
                if (DEBUG){
                    printf("Unknown option\n");
                }
                break;
            default:
                if (DEBUG){
                    printf("Default %d\n", c);
                }
                break;
        }
        
    };
    return 0;

}

unsigned long long get_available_ram(){
    return sysconf(_SC_AVPHYS_PAGES) * sysconf(_SC_PAGE_SIZE) / 1024 / 1024 / 1024;
}

unsigned long long get_total_ram(){
    return sysconf(_SC_PHYS_PAGES) * sysconf(_SC_PAGE_SIZE) / 1024 / 1024 / 1024;
}

int get_cpu_count(){
    return sysconf(_SC_NPROCESSORS_ONLN);
}

int get_current_day_name(){
    time_t t = time(NULL);
    struct tm tm = *localtime(&t);
    return tm.tm_wday;
}

int get_current_day(){
    time_t t = time(NULL);
    struct tm tm = *localtime(&t);
    return tm.tm_mday;
}

void start_gui();


int main(int argc, char *argv[], char *envp[]){

    process_options(argc, argv, envp);

    if (DEBUG){
    printf("%lld, %lld, %d\n", get_available_ram(), get_total_ram(), get_cpu_count());

    
    char *days[] = {"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"};
    printf("Today is %s, %dth day of the month\n", days[get_current_day_name()], get_current_day());
    }

    start_gui();


    return 0;
}

int generate_labyrinth(int rows, int cols) {
    int i, j;
    char maze[rows][cols];
    int start_row, start_col, end_row, end_col;

    // initialize ncurses
    initscr();
    curs_set(0); // hide the cursor
    keypad(stdscr, TRUE); // enable arrow keys
    noecho(); // don't echo user input

    // generate the maze
    srand(time(NULL)); // seed the random number generator
    for (i = 0; i < rows; i++) {
        for (j = 0; j < cols; j++) {
            if (i == 0 || j == 0 || i == rows - 1 || j == cols - 1) {
                maze[i][j] = '#'; // generate outer walls
            } else if (rand() % 10 == 0) {
                maze[i][j] = '#'; // generate inner walls randomly
            } else {
                maze[i][j] = ' '; // empty space
            }
        }
    }

    // generate start and end positions
    start_row = rand() % (rows - 2) + 1;
    start_col = rand() % (cols - 2) + 1;
    do {
        end_row = rand() % (rows - 2) + 1;
        end_col = rand() % (cols - 2) + 1;
    } while (start_row == end_row && start_col == end_col); // make sure start and end are not the same position
    maze[start_row][start_col] = 's';
    maze[end_row][end_col] = 'e';

    // print the maze
    clear();
    for (i = 0; i < rows; i++) {
        for (j = 0; j < cols; j++) {
            mvaddch(i, j, maze[i][j]);
        }
    }

    // move the cursor to the start position
    move(start_row, start_col);
    refresh();

    // handle user input and check for win condition

    // save the current position
    int current_row = start_row;
    int current_col = start_col;



    int ch;
    int next_symbol;

    while ((ch = getch()) != 'q') {
        switch (ch) {
            case KEY_UP:
                next_symbol = mvwinch(stdscr, current_row - 1, current_col);
                if (next_symbol != '#') {
                    mvaddch(current_row, current_col, ' ');
                    current_row--;
                }
                break;
            case KEY_DOWN:
                next_symbol = mvwinch(stdscr, current_row + 1, current_col);
                if (next_symbol != '#') {
                    mvaddch(current_row, current_col, ' ');
                    current_row++;
                }
                break;
            case KEY_LEFT:
                next_symbol = mvwinch(stdscr, current_row, current_col - 1);
                if (next_symbol != '#') {
                    mvaddch(current_row, current_col, ' ');
                    current_col--;
                }
                break;
            case KEY_RIGHT:
                next_symbol = mvwinch(stdscr, current_row, current_col + 1);
                if (next_symbol != '#') {
                    mvaddch(current_row, current_col, ' ');
                    current_col++;
                }
                break;
        }
        

        move(current_row, current_col);
        // set the new position to the player character
        mvaddch(current_row, current_col, '@');

        // if the player not at start set start to 's'
        if (current_row != start_row || current_col != start_col) {
            mvaddch(start_row, start_col, 's');
        }

        // if the player not at end set end to 'e'
        if (current_row != end_row || current_col != end_col) {
            mvaddch(end_row, end_col, 'e');
        }

        refresh();
        if (next_symbol == 'e') {
            break;
        }
    }
    if (ch == 'q') {
        return 0;
    }

    // print win message
    if (next_symbol == 'e') {
        mvaddstr(rows / 2, cols / 2 - 4, "You win!");
        getch();
        // endwin();
        return 1;
    }
    mvaddstr(rows / 2, cols / 2 - 4, "You lose!");
    getch();
    endwin();
    return 0;
    
}


void print_message(char *message){
    // prints a message in the middle of the screen and waits for user input
    initscr();

    // char *message = "Hello World!";
    int max_x, max_y;
    getmaxyx(stdscr, max_y, max_x);

    int message_length = strlen(message);

    mvprintw(max_y / 2, (max_x - message_length) / 2, "%s", message);
    refresh();
    getch();
    

}


// handle terminal resize
void handle_resize(int sig) {
    endwin();
    refresh();
    clear();
    
}


void start_gui(){
    // ncurses gui
    signal(SIGWINCH, handle_resize);
    initscr(); // initialize ncurses
    noecho(); // disable echoing of keys
    cbreak(); // disable line buffering
    keypad(stdscr, TRUE);
    curs_set(0);
    
    int max_y = 0;
    int max_x = 0;

    getmaxyx(stdscr, max_y, max_x);

    // print_message("Press any key to start");
    // getch();

    // if (max_x < 100 || max_y < 100 || check_system_requirements()){
    if (max_x < 10 || max_y < 10 || check_system_requirements()){
        print_message("System requirements not met");
        endwin();
        exit(1);
    }
    // check_system_requirements();
    // endwin();
    if (generate_labyrinth(max_y, max_x)){
        send_check_to_server();

    }
    
    endwin();
    
}

// build: gcc -Wall -s msr.c -o msr.elf -lncurses
