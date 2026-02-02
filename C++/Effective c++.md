# 基础
## 条款1：视c++为语言联邦
c，面向对象的c++,模板c++,STL
## 条款2:以const,enum,inline替换#define
宁可以编译器代替预处理器，即对于单纯常量，最好以const对象或enum替换#define;对于形似函数的宏，最好改用inline函数替换#define
## 条款3:尽可能用const
### const成员函数
两个成员函数如果只是常量性constness不同，可以被重载
class TextBlock{
public:
    const char& operator[](std::size_t position) const {return text[position];} //const对象
    char& operator[](std::size_t position) {return text[position];} //non-const对象
private:
    std::string text;
};

编译器强制实施bitwise constness,即const成员函数不更改对象的任何非static成员变量，除非使用mutable释放掉该约束。
### 在const和non-const成员函数中避免重复
使用static_cast将non-const对象转为const对象，调用const版本的函数，将其返回值使用const_cast移除const后返回
```
class TextBlock{
public:
    const char& operator[](std::size_t position) const {
        //实现
    } 
    char& operator[](std::size_t position) {
        return const_cast<char&>(static_cast<const TextBlock&>(*this)[position]);
    } 
private:
    std::string text;
};
```

## 条款4：确定对象被使用前已先被初始化
-  为内置对象进行手工初始化，因为c++不保证初始化它们
- 构造函数最好使用成员初值列，而不要在构造函数中使用赋值操作。初值列列出的成员变量，其排列次序应和它们在class中的声明次序相同
- 以local static对象替换non-local对象
	- static对象，其寿命从被构造出来到程序结束为止，包括global对象，定义于namespace的对象，在class内、在函数内、在file作用域内被声明为static的对象。函数内的static对象称为local static对象，因为它们相对于函数而言是local。
	- c++对于定义于不同的编译单元内的non-local static对象的初始化次序并无明确定义，因此无法保证tfs会在tempDir之前先被初始化
```
class FileSystem{
public:
    std::size_t NumDisks() const;
};
extern FileSystem tfs;

class Directory{
public:
    Directory(params);

};
Directory::Directory(params){
    std::size_t disks = tfs.NumDisks();
}
Directory tempDir(params);
```

可以将每个non-local static对象搬到自己的专属函数内（该对象在此函数内被声明为static），这些函数返回一个引用指向它所含的对象，然后用户调用这些函数，而不直接指向这些对象。因为c++保证，函数内的local static对象会在该函数被调用期间、首次遇上该对象的定义式时被初始化，因此可以保证返回的引用指向一个历经初始化的对象
```
class FileSystem{...};
FileSystem& tfs(){
    static FileSystem fs;
    return fs;
}

class Directory{...};
Directory::Directory(params){
    std::size_t disks = tfs().NumDisks();
}

Directory& tempDir(){
    static Directory td;
    return td;
}
```
# 构造/析构/赋值运算
## 条款5：了解c++默默编写并调用哪些函数
如果没有声明任何构造函数，编译器会暗自创建默认构造函数。如果没有对应函数，编译器会暗自创建拷贝构造函数、拷贝赋值函数、析构函数。其中，对于拷贝构造函数和拷贝赋值函数，编译器创建的版本只是单纯地将来源对象的每一个non-static成员变量拷贝到目标对象，即浅拷贝
## 条款6：如果不想使用编译器自动生成的函数，就该明确拒绝
c++11起，使用=delete明确禁用函数
## 条款7：为多态基类声明virtual析构函数
当derived class对象经由一个base class指针被删除，而该base class带着一个non-virtual析构函数，其结果未有定义--实际执行时通常对象的derived成分没被销毁，因此需要给base class一个virtual析构函数
class的设计目的如果不是作为base class使用，或不具备多态性，就不该声明virtual析构函数
## 条款8：别让异常逃离析构函数
析构函数绝对不要吐出异常。如果一个被析构函数调用的函数可能抛出异常，析构函数应该捕捉任何异常，然后吞下它们不传播或结束程序
```
class DBConnection{
public:
    static DBConnection& create(){
        static DBConnection instance;
        return instance;
    }
    void close();
};

class DBConn{
public:
    explicit DBConn(DBConnection& db) : m_db(db){};
    ~DBConn(){
        try {m_db.close();}
        catch(...){
            //记下对close的调用失败
            std::abort();
        }
    }
private:
    DBConnection m_db;
};

int main(){
    DBConn conn(DBConnection::create());
    return 0;
}

```
## 条款9：绝不在构造和析构过程中调用virtual函数
在derived class对象的base class构造期间，对象的类型是base class而非derived class。一旦derived class析构函数开始执行，对象内的derived class成员变量便呈现未定义值。
## 条款10：令operator=返回一个reference to *this
为了实现连锁赋值 x = ( y = ( z = a)) 赋值操作符必须返回一个reference指向操作符的左侧实参
## 条款11：在operator=中处理自我赋值
1. 增加证同测试检验是否自我赋值
```
class Bitmap{};
class Widgt{
private:
    Bitmap* m_bitmap;
};
Widgt& Widgt::operator=(const Widgt& rhs){
    if(this != &rhs){
        delete m_bitmap;
        m_bitmap = new Bitmap(*rhs.m_bitmap);
    }
    return *this;
}
```

2. 使用copy and swap
```
class Bitmap{};
class Widgt{
public:
    void swap(Widgt& rhs);
private:
    Bitmap* m_bitmap;
};

Widgt& Widgt::operator=(const Widgt& rhs){
    Widgt temp(rhs);
    swap(temp); //将*this数据和rhs数据的副本交换
    return *this;
}
```

## 条款12：复制对象时勿忘其每一个成分
- Copying函数应该确保复制对象内的所有成员变量，及所有base class成分
- 不要尝试以拷贝构造函数实现拷贝赋值函数或反之，应该将共同机能放进第三个函数init中，并由两个copying函数共同调用
# 资源管理
所谓资源就是，一旦用了它，将来必须还给系统。包括动态分配内存、文件描述器、互斥锁、网络sockets等
## 条款13：以对象管理资源
获得资源后立即放进管理对象，依赖c++的析构函数自动调用机制确保资源被释放，该观念被称为资源获得时机便是初始化时机(Resource Acquisition Is Initialization，RAII）
## 条款14：在资源管理类中小心copying行为
复制RAII对象必须一并复制它所管理的资源，常见的RAII对象copying行为：抑制copying，施行引用计数法（shared_ptr）
## 条款15：在资源管理类中提供对原始资源的访问
对原始资源的访问可能经由显式或隐式转换，一般而言显式转换get()比较安全
```
class FontHandle{};
class Font{
public:
    explicit Font(FontHandle fh) : f(fh) {}
    ~Font();
    FontHandle get() {return f;}
private:
    FontHandle f;
};
```

## 条款16：成对使用new和delete时要采取相同形式
new int[]必须delete []，new必须delete
## 条款17：以独立语句将newed对象置入智能指针
```
#include <memory>

int priority();
class Widgt;
void processWidgt(std::shared_ptr<Widgt> pw, int priority);

int main(){
    /*理论上1.new Widgt 2. priority() 3. 构造shared_ptr<Widgt>(new Widgt)
    实际编译器对语句内有重新排列的自由，2和3次序并不固定，如果priority调用异常，new Widgt返回的指针未被置入智能指针，可能导致资源泄露
    */
    processWidgt(std::shared_ptr<Widgt>(new Widgt), priority()); 
    /*编译器对跨语句操作没有自由度,应以独立语句把new对象置入智能指针
    */
    std::shared_ptr<Widgt> pw(new Widgt);
    processWidgt(pw, priority());
}

```
# 设计与声明
## 条款18：让接口容易被正确使用，不易被误用
促进正确使用的办法包括接口的一致性，以及与内置类型的行为兼容
阻止误用的方法包括建立新类型、限制类型上的操作，束缚对象值
```
class Date{
public:
    Date(int month, int day, int year);
};

//建立新类型
struct Month{
    explicit Month(int month): val(month){}
    int val;
};
struct Day{};
struct Year{};

class Date{
public:
    Date(const Month& m, const Day& d, const Year& y);
};

int main(){
    Date d(Month(5), Day(11), Year(2025))；
}

//限制值
struct Month{
public:
    static Month Jan() {return Month(1);}
    static Month Feb() {return Month(2);}
private:
    explicit Month(int month);
};
struct Day{};
struct Year{};

class Date{
public:
    Date(const Month& m, const Day& d, const Year& y);
};

int main(){
    Date d(Month::Feb(), Day(11), Year(2025));
}
```

## 条款19：设计class犹如设计type
## 条款20：宁以pass-by-reference-to-const替换pass-by-value
pass-by-reference-to-const通常比较高效，并可避免切割问题
但内置类型、STL的迭代器和函数对象更适合pass-by-value
```
/*
当一个derived class对象以by value方式传递并被视为一个base class对象，base class的copy构造函数会被调用，而造成该对象的行为像个derived class对象的特化性质全会被切割掉，仅仅留下一个base class对象
*/
#include <iostream>

class Window{
public:
    std::string name() const;
    virtual void display() const;
};
class WindowWithScrollBar : public Window{
public:
    void display() const override;
};
void printNameAndDisplay(Window w){
    std::cout << w.name() << std::endl;
    w.display();
}

int main(){
    WindowWithScrollBar w;
    printNameAndDisplay(w);
    return 0;
}
```

## 条款21：必须返回对象时，别妄想返回其reference
在返回一个reference或一个object之间抉择时，选择行为正确的那个
绝不要返回pointer或reference指向一个local stack对象，或返回reference指向一个heap-allocated对象，或返回pointer或reference指向一个local  static对象而有可能同时需要多个这个的对象
## 条款22：将成员变量声明为private
成员的封装性与成员变量内容改变时所破坏的代码数量成反比。取消一个public成员变量，所有使用它的客户码都会被破坏；取消一个proteced成员，所有使用它的derived classes都会被破坏。从封装的角度看，只有两种访问权限：private（提供封装）和其他（不提供封装）
## 条款23：宁以non-member non-friend替换member函数
以non-member non-friend替换member函数，增加封装性、机能扩充性
c++标准程序库有数十个头文件，每个头文件声明std命名空间的某些机能。但这种切割方式不适用class成员函数，因为一个class必须整体定义，不能被分割为片段
## 条款24：若所有参数皆需类型转换，请采用non-member函数

```
class Rational{


public:


Rational(int numerator = 0, int denominator = 1);


const Rational operator*(const Rational& rhs) const{


Rational result(numerator * rhs.numerator, denominator * rhs.denominator);


return result;


};


private:


int numerator;


int denominator;


};


 


int main(){


Rational result;


result = Rational(1, 2) * 2; //当参数位于参数列时，可进行隐式转换


result = 2 * Rational(1, 2); //当参数位于this对象时，不可进行隐式转换


}


使用non-member函数

class Rational{


public:


Rational(int numerator = 0, int denominator = 1);


int Numerator() const {return numerator};


int Denominator() const {return denominator};


private:


int numerator;


int denominator;


};


 


const Rational operator*(const Rational& lhs, const Rational& rhs){


return Rational(lhs.Numerator() * rhs.Numerator(), lhs.Denominator() * rhs.Denominator());


}


int main(){


Rational result;


result = Rational(1, 2) * 2; //当参数位于参数列时，可进行隐式转换


result = 2 * Rational(1, 2); //当参数位于this对象时，不可进行隐式转换


}

```

##  条款25：考虑写出一个不抛异常的swap函数

```
namespace WidgtStuff


{ 


template<typename T>


class WidgtImpl{};


 


template<typename T>


class Widgt{


public:


void swap(Widgt<T>& other) {


using std::swap;


swap(pImpl, other.pImpl);


}


private:


WidgtImpl<T>* pImpl;


};


 


template<typename T>


void swap(Widgt<T>&a , Widgt<T>& b) {a.swap(b);}



} // namespace WidgtStuff 

```

c++只允许对class template偏特化，在funtion template中偏特化不可以
# 实现

## 条款26:尽可能延后变量定义式的出现时间

延后定义直到能够给它初值实参为止
## 条款27:尽量少做转型动作
单一对象(例如一个类型为Derived对象)可能拥有一个以上的地址(例如以Base*指向它时的地址和以Derived*指向它时的地址，即会有个offset在运行期施行于Derived指针用以取得Base指针)
## 条款28:避免返回handles(引用指针和迭代器)指向对象内部
遵守该条款可以增加封装性，帮助const成员函数的行为像个const，并将dangling handles的可能性降至最低
## 条款29:为异常安全而努力是值得的
- 基本承诺：出现异常后，程序可能处于任何状态--只要该状态合法
- 强烈保证：调用强烈保证的函数后，程序状态只有两种可能：如预期般到达函数成功执行后的状态，或回到函数调用前的状态
- 不抛掷保证nothrow，承诺绝不抛出异常，因为它们总是能完成它们原先承诺的功能
copy and swap策略可以实现强烈保证，即为打算修改的对象原件做出一份副本，然后在副本上进行一切必要修改，若有任何修改动作抛出异常，原对象仍然保持未改变状态。待所有改变都成功后，再将修改过的副本和原对象在一个不抛出异常的操作中置换
## 条款30：透彻了解inlining的里里外外
- inline只是对编译器的一个申请，不是强制命令。这项申请可以通过将函数定义在class定义式中隐式提出，也可以通过inline显式提出
- template的具现化与inlining无关
- 对virtual函数的调用会使inlining落空，因为virtual意味着等待知道运行期才确定调用哪个函数，而inline意味着执行前，先将调用动作替换为被调用函数的本体
- inline函数无法随着程序库的升级而升级。如果f是inline函数，将f函数本体编进程序中，一旦决定改变f，所有用到f的客户端程序都必须重新编译。如果是non-inline函数，一旦有修改，客户端只需重新连接，远比重新编译的负担少
## 条款31：将文件间的编译依存关系降至最低
支持编译依存最小化的一般构想是：相依于声明式，不要相依于定义式。如果使用指针或引用就可以完成任务，就不要使用对象。可以只靠一个类型声明式就定义出指向该类型的引用或指针，但如果定义某类型的对象则必须用到该对象的定义式；当声明某个函数而它用到某个class时，并不需要该class的定义，即使函数以by value的方式传递该类型的参数
基于该构想的两个手段是handle class和interface class
- handle class:
```
#include <string>
#include <memory>

class PersonImpl{
public:
    PersonImpl(std::string name);
    std::string name() const;
private:
    std::string m_name;
};

class Person{
public:
    Person(const std::string& name);
    std::string name() const;
private:
    std::string m_name;
    std::shared_ptr<PersonImpl> pImpl;
};

Person::Person(const std::string& name) : pImpl(new PersonImpl(name)){}
std::string Person::name() const {return pImpl->name();}
```

- interface class的目的是详细一一描述derived class的接口，通常不带成员变量，也没有构造函数，只有一个virtual析构函数以及一组pure virtual函数用来叙述整个接口
```
#include <string>
#include <memory>

class Person{
public:
    virtual ~Person();
    virtual std::string name() const = 0;
    static std::shared_ptr<Person> create(const std::string& name);
};

class RealPerson : public Person{
public:
    RealPerson(const std::string& name) : m_name(name) {}
    ~RealPerson() override;
    std::string name() const {return m_name;}
private:
    std::string m_name;
};

std::shared_ptr<Person> Person::create(const std::string& name){
    return std::shared_ptr<Person>(new RealPerson(name));
}
```

# 继承与面向对象设计
## 条款32：确定public继承塑造出is-a关系
适用于base class的每一件事情一定也适用于derived class，因为每一个derived class对象也都是一个base class对象
## 条款33：避免遮掩继承而来的名称
为了让被遮掩的名称再见天日，可在继承类中使用using表达式 using Base::func
## 条款34：区分接口继承和实现继承
- 声明一个pure virtual函数的目的是为了让derived class只继承函数接口
- 声明impure virtual函数的目的，是让derived class继承函数接口和缺省实现
- 声明non-virtual函数的目的是为了让derived class继承函数的接口以及一份强制性实现，代表不变性凌驾特异性
## 条款35：考虑virtual函数以外的其他选择
- non-virtual interface：使用public non-virtual成员函数间接调用private virtual函数。NVI手法允许derived class重新定义virtual函数，从而赋予它们如何实现机能的控制能力，但是base class保留诉说函数何时被调用的权利。
```
class GameCharacter{
public:
    int HealthValue() const{
        int retVal = doHealthValue();
        return retVal;
    }
private:
    virtual int doHealthValue() const {...} //缺省算法，derived class可重新定义
};
```

- strategy模式：将virtual函数替换为function成员变量
```
#include <functional>

class GameCharacter;
int defaultHealthCal(const GameCharacter&);
class GameCharacter{
public:
    typedef std::function<int (const GameCharacter&)> HealthFunc;
    explicit GameCharacter(HealthFunc hcf = defaultHealthCal) : healthFunc(hcf) {}
    int healthValue() const {
        return healthFunc(*this);
    }
private:
    HealthFunc healthFunc;
};

short calHealth(const GameCharacter&);
class EyeCandyCharacter : public GameCharacter{
    explicit EyeCandyCharacter(HealthFunc hcf = defaultHealthCal) : GameCharacter(hcf) {} //调用基类构造函数间接初始化
};
```

函数是全局加载的代码段，存放在程序的.text段，是静态区域，不会因为对象的销毁而释放，没有生命周期管理机制，不能直接作为成员变量
## 条款36：绝不重新定义继承而来的non-virtual函数
- non-virtual函数如B::mf和D::mf都是静态绑定，由于pB被声明为一个指向B的指针，通过pB调用的non-virtual函数永远是B所定义的版本，即使pB指向一个类型为D的对象
```
#include <iostream>

class B{
public:
    void mf() {std::cout << "B\n";}
};

class D : public B{
public:
    void mf() {std::cout << "D\n";}
};

int main(){
    D x;
    B* pB = &x;
    D* pD = &x;
    pB->mf();
    pD->mf();
}

```
- vritual函数是动态绑定，无论通过pB或pD调用mf，都会导致调用D::mf，因为两个指针真正指向一个类型为D的对象
```
#include <iostream>

class B{
public:
    virtual void mf() {std::cout << "B\n";}
};

class D : public B{
public:
    void mf() override {std::cout << "D\n";}
};

int main(){
    D x;
    B* pB = &x;
    D* pD = &x;
    pB->mf();
    pD->mf();
}

```
## 条款37：绝不重新定义继承而来的缺省参数值
对象的静态类型是在程序中被声明时所采用的类型，动态类型是目前所指对象的类型，即动态类型可以表现出一个对象会有什么行为。
绝不不要重新定义一个继承而来的缺省参数值，因为缺省参数值都是静态绑定，但是vritual函数--唯一应该被覆写的东西--却是动态绑定
使用NVI手法，令base class的public non-virtual函数指定缺省值并调用private virtual函数，后者可被derived class重新定义
```
class Shape{
public:
    enum ShapeColor{Red, Green, Blue};
    void draw(ShapeColor color = Red) const{
        doDraw(color);
    }
private:
    virtual void doDraw(ShapeColor color) const = 0;
};

class Rectangle : public Shape{
public:
private:
    void doDraw(ShapeColor color) const override {} //子类无法调用或访问基类的private成员函数，但是可以覆写
};
```

## 条款38：通过复合塑模出has-a或“根据某物实现出”
复合：某个类型的对象内含它种类型的对象
## 条款39：明智而审慎地使用private继承
如果继承关系是private，编译器不会自动把一个继承类对象转换为一个基类对象；所有private继承的成员，都会在继承类中变成private属性
private继承意味着implementation-in-terms-of根据某物实现出。继承的目的是为了基类中已经具备的某些特性，不是因为基类对象和继承类对象存在任何观念上的关系。private继承意味着只有部分实现被继承，接口部分应略去
```
class Timer{
public:
    explicit Timer(int tickFrequency);
    virtual void onTick() const;
};

class Widgt : public Timer{
private:
    void onTick() const override;
};

当牵扯protected成员和virtual函数时，尽可能使用复合，必要时才使用private继承
class Timer{
public:
    explicit Timer(int tickFrequency);
    virtual void onTick() const;
};

class Widgt{
private:
    class WidgtTimer : public Timer{
        void onTick() const override;
    };
    WidgtTimer timer;
}; 

```
## 条款40：明智而审慎地使用多重继承
多重继承可能导致歧义，如果成员函数名称相同必须明白指出调用哪一个base class内的函数。菱形继承需要使用virtual public继承
# 模板与泛型编程
## 条款41：了解隐式接口与编译期多态
对class而言，接口是显式的，以函数签名为中心。多态则是通过virtual函数发生于运行期
对template参数而言，接口是隐式的，奠基于有效表达式。多态则通过模板具现化和函数重载解析发生于编译期
## 条款42：了解typename的双重意义
声明template参数时，前缀关键字class和typename可互换
嵌套于“取决于template参数”的东西内的名称称为嵌套从属名称。如果解析器在template中遇到嵌套从属名称，它便假设这名称不是个类型，除非在紧邻它的前一个位置放上关键字typename。但是typename不可出现在基类列内的嵌套从属类型名称前，也不可以在成员初值列中作为基类修饰符
```
template<typename T>
class Derived : public Base<T>::Nested { //base class list中不允许typename
public:
    explicit Derived(int x) : Base<T>::Nested(x){ //member initialization list中不允许typename
        typename Base<T>::Nested(x) temp;
    }
};

```
## 条款43：学习处理模板化基类内的名称
base class template有可能被特化，而特化版本可能不提供和一般性template相同的接口，因此编译器往往拒绝在模板化基类MsgSender\<Company\>中寻找继承而来的名称SendClear

```
#include <string>

class CompanyA{
public:
    void sendCleartext(const std::string& msg);
    void sendEncrypted(const std::string& msg);
};

class CompanyB{
public:
    void sendCleartext(const std::string& msg);
    void sendEncrypted(const std::string& msg);
};

class CompanyC{
public:
    void sendEncrypted(const std::string& msg);
};

template<typename Company>
class MsgSender{
public:
    void SendClear(){
        std::string msg;
        Company c;
        c.sendCleartext(msg);
    }
    void SendSecret(){
        std::string msg;
        Company c;
        c.sendEncrypted(msg);
    }
};

template<>
class MsgSender<CompanyC>{
public:
     void SendSecret(){
        std::string msg;
        CompanyC c;
        c.sendEncrypted(msg);
     }
};

template<typename Company>
class LoggingMsgSender : public MsgSender<Company>{
public:
    void sendClearMsg(){
        sendClear();
    }
};
```

解决方法:
- 在调用动作前加上this->，即this->sendClear(); 
- 使用using表达式，using MsgSender\<Company\>::sendClear;
- 明白指出被调用的函数位于base class内: MsgSender\<Company\>::sendClear();
## 条款44：将与参数无关的代码抽离template
因非类型模板参数造成的代码膨胀，往往可通过函数参数或class成员变量替换template参数而消除
```
#include <iostream>

template<typename T, std::size_t n>
class SquareMatrix{
public:
    void invert();
};

int main(){
    SquareMatrix<double, 5> sm1;
    sm1.invert();
    SquareMatrix<double, 10> sm2;
    sm2.invert();
}

#include <iostream>

template<typename T>
class SquareMatrixBase{
protected:
    SquareMatrixBase(size_t n, T* pMem) : size(n), pData(pMem) {}
    void invert(size_t n, T* pMem);
private:
    size_t size;
    T* pData;
};

template<typename T, std::size_t n>
class SquareMatrix : private SquareMatrixBase<T> {
private:
    using SquareMatrixBase<T>::invert; //避免遮掩base版的invert
    T data[n*n];
public:
    SquareMatrix() : SquareMatrixBase<T>(n, data) {}
    void invert() {this->invert(n, data);} //避免模板化基类内的函数名称被继承类遮掩
};

```
## 条款45：运用成员函数模板接受所有兼容类型
声明成员函数模板以泛化拷贝构造或泛化赋值操作时，仍需要声明正常的拷贝构造和拷贝赋值操作符
```
template<class T>
class shared_ptr{
public:
    shared_ptr(shared_ptr const& r);

    template<class Y>
    explicit shared_ptr(shared_ptr<Y> const& r);

    shared_ptr& opeartor=(shared_ptr const& r);

    template<class Y>
    shared_ptr& opeartor=(shared_ptr<Y> const &r);
};

7.6.条款46：需要类型转换时请为模板定义非成员函数
template实参推导过程中从不将隐式类型转换函数纳入考虑
template<typename T>
class Rational{
public: 
    friend const Rational operator*(const Rational& lhs, const Rational& rhs){
        return Rational(lhs.numerator * rhs.numerator, lhs.denominator * rhs.denominator);
    }
};
```

## 条款47：请使用traits class表现类型信息
### 迭代器分类
- input迭代器：只能向前移动，一次一步，只能读取所指的东西且只能读取一次,istream_iterator
- output迭代器：只能向前移动，一次一步，只能涂写所指的东西且只能涂写一次,ostream_iterator
- forward迭代器：只能向前移动，一次一步，可以读写所指的东西一次以上,unordered_map, unordered_set
- bidrectional迭代器：向前向后移动，set,multiset,map,multimap,list
- random access迭代器：在常量时间内向前向后跳跃任意距离，vector,deque,string
### traits class
traits class使得类型相关信息在编译期可用
```
//提供一个template和一组特化版本，内含类型信息
template<typename IterT>
struct iterator_traits{
    typedef typename IterT::iterator_category iterator_category;
};

//建立一组重载函数或函数模板，差异只在于traits参数，实现对应traits的操作
template<typename IterT, typename DistT>
void doAdvance(IterT& iter, DistT d, std::random_access_iterator_tag){
    iter += d;
}

template<typename IterT, typename DistT>
void doAdvance(IterT& iter, DistT d, std::bidirectional_iterator_tag){
    if (d >= 0) {while (d--) ++iter;}
    else {while (d++) --iter;}
}

template<typename IterT, typename DistT>
void doAdvance(IterT& iter, DistT d, std::input_iterator_tag){
    if (d < 0) {
        throw std::out_of_range("Negative distance");
    }
    while (d--) ++iter;
}

//建立控制函数或函数模板，调用上述重载函数模板并传递traits class提供的类型信息
template<typename IterT, typename DistT>
void advance(IterT& iter, DistT d){
    doAdvance(iter, d, typename iterator_traits<IterT>::iterator_category{});
}
```

## 条款48：template元编程
编译器必须保证所有语法路径都有效，纵使是不会执行起来的代码
# 定制new和delete
STL容器所使用的heap内存是由容器所拥有的分配器对象allocator objects管理，不是被new和delete直接管理
## 条款49：了解new-handler的行为
当operator new抛出异常以反映一个未获满足的内存需求之前，它会先调用一个客户指定的错误处理函数new-handler。为了指定该函数，需要使用set_new_handler:获得一个new_handler并返回一个new_handler的函数，其参数是个指针，指向opearator new无法分配足够内存时该被调用的函数，其返回值也是个指针，指向被调用前正在执行但马上就要被替换的new_handler函数

```
#include <iostream>


class NewHandlerHolder {


public:


explicit NewHandlerHolder(std::new_handler p) : handler(p) {}


~NewHandlerHolder() {


std::set_new_handler(handler);


}


NewHandlerHolder(const NewHandlerHolder&) = delete;


NewHandlerHolder& operator=(const NewHandlerHolder&) = delete;


private:


std::new_handler handler;


};



template<typename T>


class NewHandlerSupport {


public:


static std::new_handler set_new_handler(std::new_handler p) noexcept;


static void* operator new(std::size_t size) noexcept(false);


private:


static std::new_handler currentHandler;


};



template<typename T>


std::new_handler NewHandlerSupport<T>::set_new_handler(std::new_handler p) noexcept {


std::new_handler oldHandler = currentHandler;


currentHandler = p;


return oldHandler;


}




template<typename T>


void* NewHandlerSupport<T>::operator new(std::size_t size) noexcept(false) {


NewHandlerHolder holder(currentHandler);


void* p = std::malloc(size);


return p;


}


class Widgt : public NewHandlerSupport<Widgt>{


};



void outOfMem() {


std::cerr << "Out of Memory\n";


std::abort();


}



int main(){


Widgt::set_new_handler(outOfMem);


Widgt* p = new Widgt;


}

```

## 条款50：了解new和delete的合理替换时机

## 条款51：编写new和delete时需固守常规

operator内含一个无限循环，退出循环的方法：内存被成功分配，或new_handler函数做出如下事情（让更多内存可用、安装另一个new_handler、卸除new_handler、抛出bad_alloc异常、承认失败直接return)

operator delete应该在收到null指针时不做任何事

## 条款52：写了placement new也要写placement delete

Widgt* pw = new Widgt;共有两个函数被调用：一个是用以分配内存的operator new，一个是Widgt的默认构造函数

如果opearator new接受的参数除了size_t还有其他，即所谓的placement new
# 杂项讨论

## 条款53：重视编译器的警告

## 条款54：熟悉标准程序库

## 条款55：熟悉Boost