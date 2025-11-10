#include <iostream>
#include <random>
#include <array>
#include <vector>
#include <memory>
#include <omp.h>

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

   int get_status() {
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
      return m_status;
   }
};

class Grid {
private:
   inline static thread_local std::default_random_engine m_generator;
   inline static std::uniform_real_distribution<float> m_uniform_real_distribution;
   std::vector<std::vector<std::unique_ptr<Agent>>> m_agent_unique_ptrs;
   std::vector<std::array<int, 4>> *m_stats_ptr;


public:
   int n;
   explicit Grid(int n, std::vector<std::array<int, 4>> *stats_ptr) {
      this -> n = n;
      m_stats_ptr = stats_ptr;

      m_agent_unique_ptrs.resize(n);
      for (int i = 0; i < n; i++) {
         m_agent_unique_ptrs[i].resize(n);
         for (int j = 0; j < n; j++) {
            m_agent_unique_ptrs[i][j] = std::make_unique<Agent>(i, j);
            if (i==j) {
               m_agent_unique_ptrs[i][j]->infect();
            }
            else {
               m_agent_unique_ptrs[i][j]->make_susceptible();
            }
         }
      }
   }
   //vec.emplace_back(std::make_unique<Foo>(30));

   void update() const {
      int n_susceptible = 0;
      int n_infected = 0;
      int n_immune = 0;
      int n_killed = 0;
      for (int i = 0; i < n; i++) {
         for (int j = 0; j < n; j++) {

            bool const infected = (m_agent_unique_ptrs[i][j]->get_status() == 1);
            bool const exceeded_prop = (m_uniform_real_distribution(m_generator) >= 1-virus.infect_prop);

            if (infected and m_agent_unique_ptrs[(i-1+n)%n][(j-1+n)%n]->get_status() == 0 and exceeded_prop) {
               m_agent_unique_ptrs[(i-1+n)%n][(j-1+n)%n]->infect();
            }
            else if (infected and m_agent_unique_ptrs[(i-1+n)%n][j]->get_status() == 0 and exceeded_prop) {
               m_agent_unique_ptrs[(i-1+n)%n][j]->infect();
            }
            else if (infected and m_agent_unique_ptrs[(i-1+n)%n][(j+1)%n]->get_status() == 0 and exceeded_prop) {
               m_agent_unique_ptrs[(i-1+n)%n][(j+1)%n]->infect();
            }
            else if (infected and m_agent_unique_ptrs[i%n][(j-1+n)%n]->get_status() == 0 and exceeded_prop) {
               m_agent_unique_ptrs[i%n][(j-1+n)%n]->infect();
            }
            else if (infected and m_agent_unique_ptrs[i%n][j]->get_status() == 0 and exceeded_prop) {
               m_agent_unique_ptrs[i%n][j]->infect();
            }
            else if (infected and m_agent_unique_ptrs[i%n][(j+1)%n]->get_status() == 0 and exceeded_prop) {
               m_agent_unique_ptrs[i%n][(j+1)%n]->infect();
            }
            else if (infected and m_agent_unique_ptrs[(i+1)%n][(j-1+n)%n]->get_status() == 0 and exceeded_prop) {
               m_agent_unique_ptrs[(i+1)%n][(j-1+n)%n]->infect();
            }
            else if (infected and m_agent_unique_ptrs[(i+1)%n][j]->get_status() == 0 and exceeded_prop) {
               m_agent_unique_ptrs[(i+1)%n][j]->infect();
            }
            else if (infected and m_agent_unique_ptrs[(i+1)%n][(j+1)%n]->get_status() == 0 and exceeded_prop) {
               m_agent_unique_ptrs[(i+1)%n][(j+1)%n]->infect();
            }

            if (m_agent_unique_ptrs[i][j]->get_status() == 0) {
               n_susceptible++;
            }
            else if (m_agent_unique_ptrs[i][j]->get_status() == 1) {
               n_infected++;
            }
            else if (m_agent_unique_ptrs[i][j]->get_status() == 2) {
               n_immune++;
            }
            else if (m_agent_unique_ptrs[i][j]->get_status() == 3) {
               n_killed++;
            }
         }
      }
      m_stats_ptr->push_back({n_susceptible, n_infected, n_immune, n_killed});
   }
};

int main()
{
   int n_steps = 10;

   std::vector<std::array<int, 4>> stats;

   Grid grid(100, &stats);
   for (int i = 0; i < n_steps; i++) {
      grid.update();
   }
}