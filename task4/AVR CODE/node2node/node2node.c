/*
 * Team Id: TC#975
 * Author List: Pawan, Rishabh, Jonas, Kunj
 * Filename: node2node.c
 * Theme: Thirsty Crow
 * Functions: timer5_init(), velocity(unsigned char left_motor, unsigned char right_motor), motor_pin_config(), left_encoder_pin_config(), right_encoder_pin_config(), port_init(), left_position_encoder_interrupt_init(), right_position_encoder_interrupt_init(), adc_pin_config(), angle_rotate(unsigned int Degrees_times_of_60), buzzer_off(), buzzer_on(), right_degrees(unsigned int Degrees), left_degrees(unsigned int Degrees), right(), left(), run(), uart_tx(char data), uart_rx(), uart0_init(), init_devices(), forward(), stop(), getSensorValue(), ADC_Conversion(unsigned char Ch), adc_init(),left_60_deg,right_60_deg,check()
 * Global Variables: ShaftCountLeft, ShaftCountRight, ReqdShaftCountInt, recData, data, data_inst[100], index, Left_white_line, Center_white_line, Right_white_line, threshold, ADC_Conversion
 */


// importing necessary library to accomplish the task.

#define F_CPU 14745600
#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>
#include <math.h>
#include <string.h>

// defining communication variables

#define RX  (1<<4)
#define TX  (1<<3)
#define TE  (1<<5)
#define RE  (1<<7)

//Defining necessary variables.
volatile int last_turn_b4_stop =0;      // keeps track of last turn taken by bot before stopping
int i=0;
volatile unsigned long int ShaftCountLeft = 0;   // to keep track of left position encoder
volatile unsigned long int ShaftCountRight = 0;  // to keep track of right position encoder
volatile unsigned long int ReqdShaftCountInt=0;  // to set target shaft count required for turning or moving
unsigned char recData ='o';                      // used to store data received from xbee when rx function is called
volatile unsigned char data;                     // used to store data received from xbee when interrupt is called
unsigned char data_inst[100]; // array to store the whole path traversal instruction received from xbee
int index = 0;                                   // used to keep track and decide which traversal instruction is to be executed (to pick element form "data_inst" array)
unsigned char Left_white_line = 0;               // stores the vale of left white line sensor
unsigned char Center_white_line = 0;             // stores the vale of center white line sensor
unsigned char Right_white_line = 0;              // stores the vale of right white line sensor
int threshold = 90;                             // threshold value for white line sensor
unsigned char ADC_Conversion(unsigned char);     // function prototype


/*
 * Function Name: timer5_init()
 * Input: NONE
 * Output: PWM initialized
 * Example Call: timer5_init();
 */

void timer5_init()
{
    //PWM initialization
	TCCR5A = 0xA9;
	TCCR5B = 0x00;
	TCNT5H = 0xFF;
	TCNT5L = 0x01;
	OCR5AH = 0x00;
	OCR5AL = 0xFF;
	OCR5BH = 0x00;
	OCR5BL = 0xFF;
	OCR5CL = 0xFF;
	OCR5CH = 0x00;
	TCCR5B = 0X0B;
}


/*
 * Function Name: velocity(unsigned char left_motor, unsigned char right_motor)
 * Input: value of speed by which motor is desired to rotate
 * Output: velocity is set and hence speed of motor changes
 * Logic : L298N IN pin are given PWM as per argument values.
 * Example Call: velocity(255,255);
 */

void velocity(unsigned char left_motor, unsigned char right_motor)
{
    // set velocity to right and left motor
	OCR5AL = (unsigned char)right_motor;
	OCR5BL = (unsigned char)left_motor;

}


/*
 * Function Name: motor_pin_config()
 * Input: None
 * Output: Motor driver connected pins are initialized by setting as output, also port are set low for so motor does not rotate for now
 * Logic : Port 'A' and port 'L' pins are set logically  0 or 1 to achieve this
 * Example Call: motor_pin_config();
 */

void motor_pin_config()
{
	DDRA = 0x0F;       // pins 0,1,2,3 of port A are set as output pins
	PORTA = 0X00;      // pins 0,1,2,3 of port A initialized as low
	DDRL = 0x18;      // ENA,ENB pins of motor-driver set as output pins
	PORTL = 0x18;     // ENA,ENB pins of motor-driver initialized high
}


/*
 * Function Name: left_encoder_pin_config()
 * Input: None
 * Output: Left encoder can be used for left shaft counting.
 * Logic : Port E pins are set logically 0 or 1 to achieve this
 * Example Call: left_encoder_pin_config();
 */

void left_encoder_pin_config()
{
	DDRE  = DDRE & 0xEF;  //Set the direction of the PORTE 4 pin as input
	PORTE = PORTE | 0x10; //Enable internal pull-up for PORTE 4 pin
}


/*
 * Function Name: right_encoder_pin_config ()
 * Input: None
 * Output: Right encoder can be used for right shaft counting.
 * Logic : Port E pins are set logically 0 or 1 to achieve this
 * Example Call: right_encoder_pin_config ();
 */

void right_encoder_pin_config()
{
	DDRE  = DDRE & 0xDF;  //Set the direction of the PORTE 4 pin as input
	PORTE = PORTE | 0x20; //Enable internal pull-up for PORTE 4 pin
}


/*
 * Function Name: port_init()
 * Input: NONE
 * Output: all necessary port initialization are done
 * Logic : sequentially all initialization funcition are executed to enable all necessary ports.
 * Example Call: port_init();
 */

void port_init()
{
	DDRB=0xFF;
	timer5_init();                   //Initializing timer for PWM
	motor_pin_config();              //robot motion pins config
	left_encoder_pin_config();       //left encoder pin config
	right_encoder_pin_config();      //right encoder pin config
}


/*
 * Function Name: left_position_encoder_interrupt_init()
 * Input: NONE
 * Output: left encoder are enabled and now it can be used for shaft counting
 * Example Call: left_position_encoder_interrupt_init();
 */

void left_position_encoder_interrupt_init() //Interrupt 4 enable
{
	cli(); //Clears the global interrupt
	EICRB = EICRB | 0x02; // INT4 is set to trigger with falling edge
	EIMSK = EIMSK | 0x10; // Enable Interrupt INT4 for left position encoder
	sei();   // Enables the global interrupt
}


/*
 * Function Name: right_position_encoder_interrupt_init()
 * Input: NONE
 * Output: right encoder are enabled and now it can be used for shaft counting
 * Example Call: left_position_encoder_interrupt_init();
 */

void right_position_encoder_interrupt_init() //Interrupt 5 enable
{
	cli(); //Clears the global interrupt
	EICRB = EICRB | 0x08; // INT5 is set to trigger with falling edge
	EIMSK = EIMSK | 0x20; // Enable Interrupt INT5 for right position encoder
	sei();   // Enables the global interrupt
}


/*
 * Function Name: ISR(INT4_vect)
 * Input: Hardware interrupt due to left shaft movement
 * Output: Left shaft count is incremented by 1
 * Example Call: Called when bot left wheel is rotated, like while making a left turn or forward motion
 */

ISR(INT4_vect)
{
	ShaftCountLeft++;   //increment left shaft position count
	
}


/*
 * Function Name: ISR(INT5_vect)
 * Input: Hardware interrupt due to right shaft movement
 * Output: Right shaft count is incremented by 1
 * Example Call: Called when bot right wheel is rotated, like while making a right turn or forward motion
 */


ISR(INT5_vect)
{
	ShaftCountRight++;  //increment right shaft position count
	
}


/*
 * Function Name: adc_pin_config()
 * Input: NONE
 * Output: Port F is set as input for getting white line sensor value
 * Logic : Port F are set low to set as input.
 * Example Call: adc_pin_config();
 */


void adc_pin_config()
{
	DDRF = 0x00;       //set as input
	PORTF = 0x00;      //giving port f pins low signal

}


/*
 * Function Name: adc_init()
 * Input: NONE
 * Output: adc conversion are enabled
 * Example Call: adc_init();
 */

void adc_init()
{
    // initializing adc for white line sensor
	ADCSRA = 0x00;
	ADCSRB = 0x00;
	ADMUX = 0x20;
	ACSR = 0x80;
	ADCSRA = 0x86;
}


/*
 * Function Name: ADC_Conversion()
 * Input: channel no. (Ch), eg 1,2 or 3...or left, centre or right channel of white line sensor
 * Output: White line sensor value are returned
 * Example Call: Left_white_line=ADC_Conversion(1);
 */

unsigned char ADC_Conversion(unsigned char Ch)
{
    // converting received value from sensor to adc and return it
	unsigned char a;
    Ch = Ch & 0x07;
    ADMUX= 0x20| Ch;
    ADCSRA = ADCSRA | 0x40;
    while((ADCSRA&0x10)==0);
    a=ADCH;
    ADCSRA = ADCSRA|0x10;
    ADCSRB = 0x00;
    return a;
}


/*
 * Function Name: getSensorValue()
 * Input: NONE
 * Output: White line sensor value are stored in respective variables
 * Example Call: getSensorValue();
 */

void getSensorValue()
{
    // get and store the line sensor values
    Left_white_line=ADC_Conversion(3);
    Center_white_line=ADC_Conversion(2);
    Right_white_line=ADC_Conversion(1);
}


/*
 * Function Name: getSensorValue()
 * Input: NONE
 * Output: motor stops rotating and bot comes to rest
 * Logic: velocity is made 0 to achieve this
 * Example Call: stop();
 */

void stop()
{
	velocity(0,0);    // making velocity 0 to stop the bot
}


/*
 * Function Name: forward()
 * Input: NONE
 * Output: Bot moves forward by following the black line and stops when a node is detected
 * Logic: velocity is varied for calibrating its motion while following black line and made 0 when node is detected
 * Example Call: stop();
 */

void forward()
{
	velocity(253-140,253-130);  // velocity is initially set such that it follows black line......DIFFERENCE in VELOCITY to COMPENSATE mechanical error in forward motion
	getSensorValue();           // reading white line sensor value
	PORTA = 0x05;               // bot is set in forward motion

	while (!(Left_white_line >= threshold && Center_white_line >= threshold && Right_white_line >= threshold)) // TRUE while all sensors are NOT reading black (true until node is detected)
	{
		 
		getSensorValue();      // reading white line sensor value
		PORTA=0x05;
		if(Left_white_line <= threshold && Center_white_line <= threshold && Right_white_line >= threshold)
		{
			
			velocity(113-10,70);//(L,R)    // turning RIGHT by varying velocity to get back on black line
			
		}
		else if(Left_white_line <= threshold && Center_white_line >= threshold && Right_white_line >= threshold)
		{
			
			velocity(113-10,103);    // turning RIGHT by varying velocity to get back on black line
			
		}
		else if(Left_white_line >= threshold && Center_white_line <= threshold && Right_white_line <= threshold)
		{
			  
			velocity(70-10,113);  // turning LEFT by varying velocity to get back on black line
			
		}
		else if(Left_white_line >= threshold && Center_white_line >= threshold && Right_white_line <= threshold)
		{
			
			velocity(103-10,113);    // turning LEFT by varying velocity to get back on black line
			
		}
		else if(Left_white_line <= threshold && Center_white_line >= threshold && Right_white_line <= threshold)
		{
			 
			velocity(253-140,253-130);    // velocity difference for making rotations of right and left wheel same.
			
		}else
		{
			/* this is the condition when bot detects full white surface.
			Bot then corrects itself by re-aligning in reverse direction
			till it reads a line*/
					
			backward();
			velocity(105-10,105);
			_delay_ms(500);
			
		}
	}	
    // to make less jerk while coming to rest
	if(data_inst[0] == "P"){
		velocity(0,0);         // if pebble is just in front, bot doesn't cross the node and avoid crashing with aruco
	}
	else
	{
	_delay_ms(150);
	velocity(50-10,50);
	_delay_ms(200);
	velocity(0,0);                 // stop the bot motion
	_delay_ms(1000);	
	}
	return;
}


/*
 * Function Name: init_devices()
 * Input: NONE
 * Output: All necessary device are enabled
 * Example Call: init_devices();
 */

void init_devices()
{
	cli();                                     // clears global interrupts.
	port_init();                               // initialize all necessary ports
	left_position_encoder_interrupt_init();   // Enable left_position_encoder_interrupt
	right_position_encoder_interrupt_init();  // Enable right_position_encoder_interrupt
	DDRB= 0xFF;
	DDRH=0xFF;                                          //magnet_pin_config
	uart0_init();                             // initialize xbee communication
	adc_init();                               // initialize white line sensor
	sei();                                    // sets global interrupts.
}


/*
 * Function Name: uart0_init()
 * Input: NONE
 * Output: communication is initialized
 * Example Call: init_devices();
 */

void uart0_init()
{
	UCSR0B = 0x00;                            //disable while setting baud rate
	UCSR0A = 0x00;
	UCSR0C = 0x06;
	UBRR0L = 0x5F;                             //9600BPS at 14745600Hz
	UBRR0H = 0x00;
	UCSR0B = 0x98;
	UCSR0C = 3<<1;                            //setting 8-bit character and 1 stop bit
	UCSR0B = RX | TX;
}


/*
 * Function Name: uart_rx()
 * Input: NONE
 * Output: received data over xbee is returned
 * Example Call: recData = uart_rx();
 */

char uart_rx()
{
	while(!(UCSR0A & RE));						//waiting to receive
	return UDR0;
}


/*
 * Function Name: uart_tx(char data)
 * Input: Data to be transmitted
 * Output: data is transmitted to the remote xbee
 * Example Call: recData = uart_tx('J');
 */

void uart_tx(char data)
{
    while(!(UCSR0A & TE));                        //waiting to transmit
    UDR0 = data;
}

/*
 * Function Name: ISR(USART0_RX_vect)
 * Input: Hardware interrupt when a data is be recieved
 * Output: Data from remote xbee is recieved
 * Example Call: When bot xbee is waiting for remote xbee to send data
 */


ISR(USART0_RX_vect)
{
	data = UDR0;
}


/*
 * Function Name: run()
 * Input: NONE
 * Output: Complete traversal of bot from stating point to the last destination point is achieved
 * Logic: Traversal command is fetched from the 'data_inst'array and then executed, this process is done until final destination is acieved
 * Example run();
 */

void run()
{
    // giving explicit forward motion to bot to leave the staring point and reach the nearest node (node in front of start point)
	
	velocity(113,123);
	PORTA = 0x05;  // forward
	_delay_ms(420);
	forward();
    index = 0;
    // ShaftCountLeft or ShaftCountRight increments every time wheels rotates. so it is necessary to clear this variable so that count for degree_turn is properly obtained
    ShaftCountLeft=0;
    ShaftCountRight=0;
    while (!(data_inst[index] == '.'))     // WHEN '.' is the index element of array it would IMPLY TRAVERSAL IS COMPLETED, now break the loop and stop
    {
        if((data_inst[index] == 'w'))      // WHEN 'w' is the index element of array it would IMPLY BOT TO GO FORWARD
        {
            forward();
        }
        else if((data_inst[index] == 'a')) // WHEN 'a' is the index element of array it would IMPLY BOT TO MAKE A LEFT 60 DEGREE TURN
        {
            left_degrees(); // 60 deg
			_delay_ms(300);

			if(Center_white_line <= threshold ){  // Calibrating bot position after rotation
				right_degrees();
			}
        }
        else if((data_inst[index] == 'd'))
        {
            right_degrees();     // WHEN 'd' is the index element of array it would IMPLY BOT TO MAKE A RIGHT 60 DEGREE TURN
			_delay_ms(300);

			if(Center_white_line <= threshold ){  // Calibrating bot position after rotation
			left_degrees();
		}
        }
        else if((data_inst[index] == 's')) // WHEN 's' is the index element of array it would IMPLY BOT TO MAKE A 180 DEGREE TURN (U-Turn)
        {
            left_degrees();  // 60 deg
			left();
			_delay_ms(700);
			left_degrees();   //60
			_delay_ms(700);
			
			getSensorValue();
			
			if(!(Left_white_line <= threshold && Center_white_line >= threshold && Right_white_line <= threshold))
			{
				right_degrees(); // to compensate extra turn 
			}				
		}
        else if((data_inst[index] == 'W')) // WHEN 'W' is the index element of array it would IMPLY BOT TO GO A BIT FORWARD
        {
            //forward_mm(40); //move a bit ahead to reach pick/drop point
			_delay_ms(100);
			velocity(253-140,253-130);
			PORTA=0x05;
			
			_delay_ms(450);
			velocity(0,0);
			_delay_ms(500);
			buzzer_off();
			
        }
        else if((data_inst[index] == 'A')) // WHEN 'A' is the index element of array it would IMPLY BOT TO MAKE A LEFT 120 DEGREE TURN
        {
			
			
			left_degrees(); // 60 deg
			_delay_ms(50);
			left_60_deg(); // hard rotate 60 degrees left
			_delay_ms(500);
			

		}
        else if((data_inst[index] == 'D')) // WHEN 'A' is the index element of array it would IMPLY BOT TO MAKE A Right 120 DEGREE TURN
        {
			
			right_degrees(); // 60 deg
			_delay_ms(50);
			right_60_deg(); // hard rotate 60 degrees right
			_delay_ms(500);
		}
        else if((data_inst[index] == 'S')) // WHEN 'A' is the index element of array it would IMPLY BOT TO move backward a bit
        {
             // to go back to node from the pick/drop point
				_delay_ms(100);
				velocity(253-140,253-130);
				PORTA=0x0A;
				ShaftCountRight=0;
				
				_delay_ms(450);
				velocity(0,0);
        }
        else if((data_inst[index] == 'P')) // WHEN 'P' is the index element of array it would IMPLY BOT TO PICK PEBBLE AND ALSO COMMUNICATE REMOTE XBEE FOR AR ANIMATION
        {
            magnet_on(); // make the port high for magnet
			
			_delay_ms(1000); // give some time for charging 
			
			
			
			uart_tx('J');    // will inform the pc to change AR of pebble
		    recData = uart_rx();
			uart_tx(recData);
			if (recData == 'c'){
				// the communication was established
				// do nothing
			}
			
			
			
             // the pebble is diminished
        }
        else if((data_inst[index] == 'T')) // WHEN 'P' is the index element of array it would IMPLY BOT TO DROP PEBBLE AND ALSO COMMUNICATE REMOTE XBEE FOR AR ANIMATION
        {
			

			uart_tx('K'); //communicate pc to change water level (AR)
			
			recData = uart_rx();
			uart_tx(recData);
			if (recData == 'c'){
				// the communication was established
				// do nothing
			}
			
			
            magnet_off();
			_delay_ms(2000);

        }
        else if((data_inst[index] == 'z')) // WHEN 'P' is the index element of array it would IMPLY BOT TO TURN ON BUZZER
        {
            buzzer_on();          //will be used in finals to add depict completion of whole arena traversal.
			_delay_ms(5000);
        }
        else if((data_inst[index] == 'Z')) // WHEN 'P' is the index element of array it would IMPLY BOT TO TURN OFF BUZZER
        {
            buzzer_off(); // end of whole traversal
        }

        index = index + 1;  // will point to next instruction in array
    }
		stop();  // stop the bot
}


/*
 * Function Name: left()
 * Input: NONE
 * Output: left wheel moves backward and right wheel moves forward
 * Logic : port A pins are made logically 0 and 1 to achieve this.
 * Example Call: right();
 */

void left()
{
	velocity(253-140,253-130);
	PORTA = 0x09;
}

/*
* Function Name: right()
* Input: NONE
* Output: left wheel moves forward and right wheel moves backward
* Logic : port A pins are made logically 0 and 1 to achieve this.
* Example Call: right();
*/

void right()
{
	velocity(253-140,253-130);
	PORTA = 0x06;
}

/*
* Function Name: backward()
* Input: NONE
* Output: left wheel moves backward and right wheel moves backward
* Logic : port A pins are made logically 0 and 1 to achieve this.
* Example Call: backward();
*/

void backward()
{
	PORTA = 0x0A;
}


/*
 * Function Name: left_degrees(unsigned int Degrees)
 * Input: Left degrees to be rotated
 * Output: left wheel moves forward and right wheel moves backward
 * Logic : Bot makes left turn and shaft count helps determine its angle of rotation .
 * Example Call: left_degrees(160);
 */

void left_degrees()
{
	
	left(); //Turn left
	angle_rotate();
}


/*
 * Function Name: right_degrees(unsigned int Degrees)
 * Input: Right degrees to be rotated
 * Output: left wheel moves backward and right wheel moves forward
 * Logic : Bot makes right turn and shaft count helps determine its angle of rotation .
 * Example Call: right_degrees(160);
 */


void right_degrees()
{
	
	right(); //Turn right
	angle_rotate();
}


/*
 * Function Name: buzzer_on()
 * Input: NONE
 * Output: Turns buzzer on
 * Logic : making port B pin high
 * Example Call: buzzer_on();
 */

void buzzer_on()
{
    PORTB= 0xFF;
}


/*
 * Function Name: buzzer_off()
 * Input: NONE
 * Output: Turns buzzer off
 * Logic : making port B pin low
 * Example Call: buzzer_off();
 */

void buzzer_off()
{
	PORTB= 0x00;
}


/*
 * Function Name: magnet_on()
 * Input: None
 * Output: bot energizes the magnet
 * Logic : making port H pin high
 * Example Call: magnet_on();
 */

magnet_on(){
	
	PORTH=0xFF;
}


/*
 * Function Name: magnet_off()
 * Input: None
 * Output: bot energizes the magnet
 * Logic : making port H pin low
 * Example Call: magnet_off();
 */

magnet_off(){
	
	PORTH=0x00;
}

/*
 * Function Name:angle_rotate()
 * Input: None
 * Output: bot rotated till it reads a black line
 * Logic : when center sensor reads black and Left & Right sensor reads white, bot stops rotating (this mainly helps us achieve 60 deg for sure)
 * Example Call: angle_rotate();
 */

void angle_rotate()
{

	while(1){
		getSensorValue();
		if(Left_white_line <= threshold && Center_white_line >= threshold && Right_white_line <= threshold){
			velocity(0,0);
			break;
		}
	}

    stop(); //Stop robot
}

/*
* Function Name:check()
* Input: None
* Output: bot moves for 0.5 sec
* Logic : None
* Example Call: check();
*/

void check(){
	
	_delay_ms(500); // be in last position for 0.5 seconds (mostly used for rotation)
}

/*
* Function Name:right_60_deg()
* Input: None
* Output: bot moves till it achieves 60 deg right turn
* Logic : With the help of velocity and dimension of bot, it is possible to achieve its angular turn period. In our case it is 0.5 sec for 60 deg turn
* Example Call: right_60_deg();
*/


void right_60_deg(){
	ShaftCountRight=0; // reset shaft count
	velocity(120,130);
	PORTA = 0x06;    // right turn
	check();         // check for 60 degree rotation
	velocity(0,0);   // stop
	ShaftCountRight=0; // reset shaft count for safer side

}

/*
* Function Name:left_60_deg()
* Input: None
* Output: bot moves till it achieves 60 deg left turn
* Logic : With the help of velocity and dimension of bot, it is possible to achieve its angular turn period. In our case it is 0.5 sec for 60 deg turn
* Example Call: left_60_deg();
*/


void left_60_deg(){
	ShaftCountRight=0; // reset shaft count
	velocity(120,130);
	PORTA = 0x09;   // left turn
	check();        // check for 60 degree rotation
	velocity(0,0);  // stop
	ShaftCountRight=0; // reset shaft count for safer side
	
}


//MAIN FUNCTION

int main(void)
{

	init_devices();  // initialing devices

	

	while(1){
        recData = uart_rx();              // storing received data ( all the traversal instructions in form of mnemonics
		data_inst[index]=recData;         //appending  the  instructions
		uart_tx(recData);                 // transmitting back to cross check and confirm that all instructions are received
		if(recData=='.')
        {
            break;
		}
		else
        {
            index+=1;
		}
    }
  
	

_delay_ms(200); // just some delay
run();          // start the traversal




    



}
