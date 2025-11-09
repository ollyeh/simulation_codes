#include <iostream>
#include <random>
#include <array>
#include <memory>

struct Virus
{
   float mean_contagious_period = 100;
   float sdev_contagious_period = 3;
   float mean_immune_period = 50;
   float sdev_immune_period = 10;
   float kill_prop = 0.001;
   float infect_prop = 0.1;
};

constexpr Virus virus;
constexpr size_t n = 5;

class Agent {
private:
   int m_status = 0;
   int m_contagious_counter = 0;
   int m_immune_counter = 0;

   int m_contagious_period = 0;
   int m_immune_period = 0;

   //
   inline static thread_local std::default_random_engine m_generator;
   inline static std::normal_distribution<float> m_contagious_distribution{virus.mean_contagious_period, virus.sdev_contagious_period};
   inline static std::normal_distribution<float> m_immune_distribution{virus.mean_immune_period, virus.sdev_immune_period};
   inline static std::uniform_real_distribution<float> m_uniform_real_distribution;

public:
   int x;
   int y;

   Agent(int x, int y) {
      this ->x = x;
      this ->y = y;
   }

   void make_susceptible() {
      m_contagious_counter = 0;
      m_status = 0;
   }

   void infect() {
      m_status = 1;
   }

   void immunize() {
      m_status = 2;
   }

   void kill() {
      m_status = 2;
   }

   void get_status() {
      // pick time periods from normal distributions
      int m_contagious_period = m_contagious_distribution(m_generator);
      int m_immune_period = m_immune_distribution(m_generator);

      // increase contagious counter by 1
      if (m_status == 1 and m_contagious_counter < m_contagious_period) {
         m_contagious_counter++;
      }
      else if (m_status == 1 and m_contagious_counter >= m_contagious_period) {
         (m_uniform_real_distribution(m_generator) >= 1 - virus.kill_prop) ? kill() : immunize();
         m_contagious_counter = 0;
      }
      else if (m_status == 2 and m_immune_counter < m_immune_period) {
         m_immune_counter++;
         if (m_immune_counter >= m_immune_period) {
            make_susceptible();
            m_immune_counter = 0;
         }
         else {
            (void)0;
         }
      }
   }
};

class Grid {
private:
   std::array<std::array<std::unique_ptr<Agent>, n>, n> m_agent_ptrs;
public:
   explicit Grid() {
      for (int i = 0; i < n; i++) {
         for (int j = 0; j < n; j++) {
            Agent agent(i, j);
            m_agent_ptrs[i][j] = std::make_unique<Agent>(agent);
            if (i==j) {
               agent.infect();
            }
            else {
               agent.make_susceptible();
            }
         }
      }
   }

};

int main()
{
   Agent agent(3, 3);
   agent.get_status();
   agent.get_status();
   agent.get_status();
   agent.get_status();
   agent.get_status();
   Grid grid;
}