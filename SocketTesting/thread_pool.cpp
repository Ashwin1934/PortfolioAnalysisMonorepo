#include <thread>
#include <vector>
#include <iostream>
#include <queue>

// class Task {
//     public:
//         void operator()() {
//             std::cout << "hello from subthread." << std::endl;
//         }

// };

class ThreadPool {
    private:
        unsigned int num_processors = std::thread::hardware_concurrency();
        std::vector<std::thread> worker_threads;
        //std::queue<Task> queue;
        std::queue<int> queue;

        void worker_thread_task(int num) {
            std::cout << "thread task completed: " << num * num << std::endl;
        }
        
       
    public:

        ThreadPool() { // default constructor, thread pool size = number of processors
            ThreadPool(num_processors);
        }

        ThreadPool(unsigned int num_threads) {
            for (unsigned int i = 0; i < num_threads; i++) {
                worker_threads.emplace_back(new std::thread);
            }
            processTasks();
        }

        void submitTask(int task) {
            //queue.push(std::move(t));
            queue.push(task);
        }

        void processTasks() {
            //while (!queue.empty()) { // needs to be another hook, cuz if no tasks the loop will stop
            while(true) {
                while (!queue.empty()) {
                    int task = queue.front();
                    queue.pop();

                    // iterate through all the threads, check for which thread is not occupied
                    for (auto& thread: worker_threads) {
                        // a thread is joinable if it is executing a task and can be joined with the current line of execution
                        // so, we are looking for a thread that is not joinable, or not occupied, to take on the task
                        if (!thread.joinable()) {
                            // submit the task to the thread
                            std::thread currThread(worker_thread_task, task);
                            currThread.join(); // join the thread so that it is now occupied
                        }
                    }
                }

            }
            //}
        }

        ~ThreadPool() {
            // what goes in here? do we need to deallocate memoryh for the threads or the queue at least?
            // also need a hook of some sort to shut down the queue
        }


};