# 1 仿函数
仿函数即重载了()运算符的对象，看起来像函数一样调用
```
struct Point{
    double x, y;
};

struct Compare{
    bool operator()(const Point& p1, const Point& p2) const noexcept;
};

bool Compare::operator()(const Point& p1, const Point& p2) const noexcept{
    return p1.x < p2.x && p1.y < p2.y;
}

int main(){
    Point p1{1, 2}, p2{3, 4};
    Compare compare;
    std::cout << compare(p1, p2) << std::endl;
}
```
```
#include <iostream>

template<typename T, template<typename> typename Compare> //模板模板参数
void Sort(T* arr, size_t size){
    for (int i = 0; i < size; i ++){
        for (int j = i + 1; j < size; j++){
            if (Compare<T>{}(arr[j], arr[i])){
                T temp = arr[i];
                arr[i] = arr[j];
                arr[j] = temp;
            }
        }
    }
}

//Less<int> 是一个可以调用的对象
template<typename T>
struct Less{
    bool operator()(const T& l, const T& r) const noexcept{
        return l < r;
    }
};

template<typename T>
struct Great{
    bool operator()(const T& l, const T& r) const noexcept{
        return l > r;
    }
};
int main(){
   int arr[] {2, 3, 1, 4, 5};
   Sort<int, Great>(arr, 5);
   for(auto i : arr)
    std::cout << i << " ";
}
```

# 2 lambda
本质是编译器自动生成的一个临时的仿函数对象（Functor）。
```
#include <iostream>
#include <vector>
#include <algorithm>

template <typename T, typename Compare>
bool IsMatch(const std::vector<T>& v, const Compare& com = Compare{}){
    for (const auto& item : v){
        if (com(item))
            return true;
    }
    return false;
}

template<typename T>
struct CompareFlag{
    bool operator()(const T& item) const{
        return item < val_;
    }
    CompareFlag(const T& val) : val_(val){}
private:
    const T& val_;
};

void Demo1(int flag){
    std::vector<int> vec{1, 3, -1, 0, -9};
    CompareFlag<int> cf{flag};
    bool is_match = IsMatch<int, CompareFlag<int>>(vec, cf);
    std::cout << is_match << std::endl;
}

void Demo2(int flag){
    std::vector<int> vec{1, 3, -1, 0, 9};
    auto iter = std::find_if(vec.begin(), vec.end(), [flag](int item)->bool{return item < flag;}); //lambda表达式，编译器自动生成一个匿名类并实例化为仿函数对象
    std::cout << *iter << std::endl;
}
```

如果lamda中含有捕获，捕获的外部变量会被储存为匿名仿函数类的成员变量。由于函数指针只能指向普通函数，而不能指向带有成员变量的对象，因此带捕获的lambda不能隐式转换成函数指针。STL的函数对象std::fucntion可以封装各种可调用对象，不仅支持函数指针直接构造，也支持含有捕获列表的lambda表达式
```
#include <iostream>
#include <functional>

template<typename T>
T* FindIf(T* arr, size_t size, std::function<bool (const T&)> is_match){
    for (T* item = arr; item < arr + size; item++){
        if (is_match(*item))
            return item;
    }
    return nullptr;
}

void Demo(int flag){
    int arr[] {1, -3, 5, 0, -9, 2};
    auto is_match = [flag](const int& item) {return item < flag;};
    auto p = FindIf<int>(arr, 5, is_match);
    if (p != nullptr)
        std::cout << *p << std::endl;
}
```

类内的lambda如果需要访问成员变量或者成员函数，必须捕获this（或者使用默认捕获[=]）。[this]是捕获this指针本身，不是拷贝整个对象内容，如果外部对象销毁，lambda里再访问this就会悬空
```
#include <iostream>
#include <functional>
#include <algorithm>

template<typename T>
T* FindIf(T* arr, size_t size, std::function<bool (const T&)> is_match){
    for (T* item = arr; item < arr + size; item++){
        if (is_match(*item))
            return item;
    }
    return nullptr;
}

struct Test{
    int a, b;
    void f1(){}
    void f2();
};

void Test::f2(){
    int arr[] {1, 3, -2, 5, 4};
    int v = 5;
    auto p = FindIf<int>(arr, 5, [v, this](const int& item)->bool {
        f1();
        return item < v && item < a;});
    std::cout << *p << std::endl;
}

int main(){
    Test test{};
    test.f2();
}
```