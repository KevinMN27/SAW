#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

using namespace std;

// Clase que representa una restricción (criterio)
class Criterion {
public:
    string name;  // Nombre y tipo de la restricción
    double weight;     // Peso de la restricción
    string type;

    Criterion(const string& name, double weight, const string& type) : name(name), weight(weight), type(type) {}
};

// Clase que representa una alternativa
class Alternative {
public:
    string name;                       // Nombre de la alternativa
    vector<double> values;             // Valores asociados a cada restricción
    vector<double> normalizedValues;   // Valores normalizados

    Alternative(const string& name, const vector<double>& values)
        : name(name), values(values) {}

    // Normalización de valores para cada restricción
    void normalize(const vector<double>& maxValues, const vector<double>& minValues, const vector<Criterion>& criteria) {
        normalizedValues.clear();
        for (size_t i = 0; i < values.size(); ++i) {
            if (criteria[i].type == "benefit") {
                normalizedValues.push_back(values[i] / maxValues[i]);
            } else {
                normalizedValues.push_back(minValues[i] / values[i]);
            }
        }
    }
};

// Clase que implementa el algoritmo SAW
class SAW {
private:
    vector<Criterion> criteria;         // Lista de criterios (restricciones)
    vector<Alternative> alternatives;   // Lista de alternativas

public:
    // Agregar un criterio
    void addCriterion(const string& name, double weight, const string& type) {
        criteria.emplace_back(name, weight, type);
    }

    // Agregar una alternativa
    void addAlternative(const string& name, const vector<double>& values) {
        alternatives.emplace_back(name, values);
    }

     // Método que realiza el cálculo de SAW y devuelve el índice de la mejor alternativa
    int calculateBestAlternative() {
        vector<double> maxValues(criteria.size(), 0);
        vector<double> minValues(criteria.size());

        // Encontrar los valores máximos de cada criterio para normalizar
        for (size_t i = 0; i < criteria.size(); ++i) {
            unsigned int j = 0;
            for (const auto& alternative : alternatives) {
                maxValues[i] = max(maxValues[i], alternative.values[i]);
                minValues[i] = (j < 1) ? alternative.values[i] : min(minValues[i], alternative.values[i]);
                j++;
            }
        }

        // Normalizar valores para cada alternativa
        for (size_t i = 0; i < alternatives.size(); ++i) {
            alternatives[i].normalize(maxValues, minValues, criteria);
        }

        // Calcular el puntaje de cada alternativa usando el método SAW
        double bestScore = -1;
        int bestAlternativeIndex = -1;  // Cambiar para devolver el índice
        unsigned int j = 0;
        for (auto& alternative : alternatives) {
            double score = 0.0;
            for (size_t i = 0; i < criteria.size(); ++i) {
                score += alternative.normalizedValues[i] * criteria[i].weight;
            }
            // Buscar la alternativa con el mejor puntaje
            if (score > bestScore) {
                bestScore = score;
                bestAlternativeIndex = j;  // Guardar el índice de la mejor alternativa
            }
            j++;
        }

        // Devolver el índice de la mejor alternativa
        return bestAlternativeIndex;
    }
};

int main() {
    SAW decisionModel;

    // Definir los criterios (restricciones) con sus respectivos pesos
    /*decisionModel.addCriterion("Logros", 5, "cost");
    decisionModel.addCriterion("Ambiente", 4, "benefit");
    decisionModel.addCriterion("Acreditacion", 3, "cost");
    decisionModel.addCriterion("Curriculum", 2, "benefit");
    decisionModel.addCriterion("ExtraAct", 1, "benefit");

    // Definir las alternativas y sus valores asociados a cada criterio
    decisionModel.addAlternative("Alternativa 1", { 4, 2, 4, 2, 2 });
    decisionModel.addAlternative("Alternativa 2", { 2, 3, 3, 2, 1 });
    decisionModel.addAlternative("Alternativa 3", { 2, 3, 3, 1, 2 });
    decisionModel.addAlternative("Alternativa 4", { 4, 1, 3, 1, 1 });

    // Calcular y mostrar la mejor alternativa
    Alternative bestAlternative = decisionModel.calculateBestAlternative();
    cout << "La mejor alternativa es: " << bestAlternative.name << endl;
    */
    return 0;
}

SAW decisionModel;

extern "C" {
    // Función para agregar un criterio
    void add_criterion(const char* name, double weight, const char* type) {
        decisionModel.addCriterion(name, weight, type);
    }

    // Función para agregar una alternativa
    void add_alternative(const char* name, double* values, int length) {
        vector<double> vals(values, values + length);
        decisionModel.addAlternative(name, vals);
    }

    // Función para calcular la mejor alternativa
    int calculate_best_alternative() {
        return decisionModel.calculateBestAlternative();
    }
}