# KDTree
# DBSCAN
# 代码实现
```
#include <iostream>

#include <cmath>

#include <functional>

#include <vector>

  

struct Point {

    double x, y, z;

    int cluster_id = -1;

};

  

struct KDNode {

    Point pt;

    KDNode* left;

    KDNode* right;

    int axis; // 0 for x, 1 for y, 2 for z

    KDNode(const Point& p, int a) : pt(p), left(nullptr), right(nullptr), axis(d) {}

};

  

class KDTree {

public:

    KDNode* root;

    int dim;

    KDTree(const std::vector<Point>& points, int dimension = 3) : dim(dimension) {

        std::vector<Point> pts = points;

        root = buildTree(pts, 0);

    }

  

    KDNode* buildTree(std::vector<Point>& points, int depth) {

        if (points.empty()) return nullptr;

  

        int axis = depth % dim;

        auto compare = [axis](const Point&a, const Point& b) {

            if (axis == 0)

                return a.x < b.x;

            else if (axis == 1)

                return a.y < b.y;

            else

                return a.z < b.z;

        };

        std::sort(points.begin(), points.end(), compare);

        int median = points.size() / 2;

        std::vector<Point> left(points.begin(), points.begin() + median);

        std::vector<Point> right(points.begin() + median + 1, points.end());

        KDNode* node = new KDNode(points[median], axis);

        node->left = buildTree(left, depth + 1);

        node->right = buildTree(right, depth + 1);

        return node;

    }

  

    void search(KDNode* node, const Point& target, double radius, std::vector<int>& result_idx, const std::vector<Point>& points) {

        if (!node) return;

  

        double dist = std::sqrt(std::pow(node->pt.x - target.x, 2) +

                                std::pow(node->pt.y - target.y, 2) +

                                std::pow(node->pt.z - target.z, 2));

        if (dist <= radius) {

            for (int  i = 0; i < points.size(); ++i) {

                if (&points[i] == &node->pt) {

                    result_idx.push_back(i);

                    break;

                }

        }

  

        double diff = (node->axis == 0) ? (target.x - node->pt.x) :

                      (node->axis == 1) ? (target.y - node->pt.y) :

                                    (target.z - node->pt.z);

        if (diff <= radius) {

            search(node->left, target, radius, result_idx, points);

        }

        if (diff >= -radius) {

            search(node->right, target, radius, result_idx, points);

        }

    }    

};
```