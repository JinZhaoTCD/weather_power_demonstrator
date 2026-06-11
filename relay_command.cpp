#include <usbrelay.hpp>
#include <iostream>
#include <string>


void printStatus(Usbrelay *usbrelay){ //Format for terminal usb board relays status
    std::cout<<"=====Board Status====="<<std::endl;
    char status= usbrelay->getState();
    int relaynumber = usbrelay->getRelayNumber();

    for(int i=1;i<=relaynumber;i++){
        int kstate = status & 1;
        status = status >> 1; 
        if(kstate){
            std::cout<<"K"+std::to_string(i)+": "+"ON"<<std::endl;
        }
        else{
            std::cout<<"K"+std::to_string(i)+": "+"OFF"<<std::endl;
        }
    }
}


int main(){
// for manual intialize after power break
    auto devicescan = scanBoard(); //Scan online COM or /dev/tty... device 
    std::cout << "=====Scanned Device=====" << std::endl; 
    for( auto device : devicescan){
        std::cout << device << std::endl;
    }
    
    //Connection and init to the board
    std::cout << "=====Connection======" << std::endl;
    
    Usbrelay* usbrelay = new Usbrelay("/dev/ttyUSB0",4); //Create a new board, please specify: port, default relaynumber
    
    if(usbrelay->openCom()!=1){//Open commmunication with the board
        std::cout << "Connection Failed" << std::endl;
    }
    string choice;
    std::cout << "Board Already initialized?(y/n):";
    std::cin >> choice;
    if(choice == "N" || choice == "n"){
        if (usbrelay->initBoard()!=1){ //Init communication protocol with the board, can be initialized only once after power reset
            std::cout << "Init Failed" << std::endl;
                }
    }
    
    int default_state[] = {0,1,0,0};
    int r_state[]       = {1,0,0,0};
    int y_state[]       = {0,0,1,0};

    if (usbrelay->setState(default_state) != 1)
    {
        std::cerr << "DEFAULT_FAIL" << std::endl;
    }

    std::cout << "READY" << std::endl;

    std::string cmd;

    while (std::getline(std::cin, cmd))
    {
        int rc = -1;
        if (cmd == "r"){
            rc = usbrelay->setState(r_state);
        }
        else if (cmd == "y"){
            rc = usbrelay->setState(y_state);
        }
        else if (cmd == "d"){
            rc = usbrelay->setState(default_state);
        }
        else if (cmd == "k"){
            break;
        }
        else
        {
            std::cout << "WAITING" << std::endl; 
        }
    }

    usbrelay->closeCom();
    return 0;
}


